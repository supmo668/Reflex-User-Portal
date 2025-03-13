import os
import uuid, yaml

import reflex as rx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from supabase import create_client, Client
import yaml
from reflex_user_portal.models.admin_config import AdminConfig, MODEL_FACTORY
import json

class BaseState(rx.State):
    query_component_toggle: str = "none"
    is_request: str = "New Request"

    def toggle_query(self):
        self.query_component_toggle = (
            "flex" if self.query_component_toggle == "none" else "none"
        )

        self.is_request = (
            "New Request" if self.query_component_toggle == "none" else "Close Request"
        )
        


class QueryState(BaseState):
    # Database connection settings
    supabase_url: str = os.getenv("SUPABASE_DB_URL", "")
    supabase_token: str = os.getenv("SUPABASE_DB_TOKEN", "")
    
    # Table selection
    available_tables: list[str] = ["admin_config"]
    current_table: str = "admin_config"
    
    # Data storage
    table_data: list[dict[str, Any]] = []
    paginated_data: list[dict[str, str]] = []
    
    # Pagination
    number_of_rows: int = 0
    limits: list[str] = ["10", "20", "50"]
    current_limit: int = 10
    offset: int = 0
    current_page: int = 1
    total_pages: int = 1
    
    # Connection status
    is_connected: bool = False

    @rx.var
    async def connection_status(self) -> str:
        """Check if connection to Supabase is successful. (only API client)"""
        if not self.supabase_url or not self.supabase_token:
            self.is_connected = False
            return "Not configured"
        try:
            client = create_client(self.supabase_url, self.supabase_token)
            # If client creation succeeds without error, we're connected
            self.is_connected = True
            return "Connected to Supabase via API: {self.supabase_url} "
        except Exception:
            self.is_connected = False
            return "Connecting..."
    
    @rx.event
    async def update_db_url(self, value: str):
        self.supabase_url = value
            
    @rx.event
    async def update_db_key(self, value: str):
        self.supabase_token = value
        
    @rx.event
    async def select_table(self, table: str):
        """Select a table to query."""
        self.current_table = table
    
    @rx.var
    async def table_headers(self) -> List[str]:
        """Get headers for the selected table."""
        model = MODEL_FACTORY.get(self.current_table)
        if model:
            return [column.name for column in model.__table__.columns]
        return []

class QueryAPI(QueryState):
    # Row editing state
    is_open: bool = False
    readonly_fields: list[str] = ["id", "created_at", "last_updated"]
    selected_entry: Dict[str, str] = {}
    original_entry: Dict[str, str] = {}
    error_message: str = ""
    show_error: bool = False
    
    async def get_supabase_client(self) -> Client:
        """Get Supabase client instance."""
        return create_client(self.supabase_url, self.supabase_token)
        
    async def clear_error(self) -> None:
        """Clear any error message and hide the alert dialog."""
        self.error_message = ""
        self.show_error = False
        
    async def handle_error_ok(self) -> None:
        """Handle OK button click in error dialog."""
        await self.clear_error()
        
    async def show_error_message(self, message: str) -> None:
        """Show an error message in the alert dialog.
        
        Args:
            message: Error message to display
        """
        print(f"Error: {message}")
        self.error_message = str(message)
        self.show_error = True
        
    async def reset_state(self) -> None:
        """Reset the drawer state."""
        self.is_open = False
        self.selected_entry = {}
        self.original_entry = {}
        await self.clear_error()
    
    @rx.event
    async def refresh_table_data(self):
        """Refresh table data from database."""
        with rx.session() as session:
            model = MODEL_FACTORY.get(self.current_table)
            print(f"Fetching model: {model}")
            if model:
                data = session.query(model).all()
                self.table_data: list[dict[str, Any]] = [{
                    column.name: getattr(item, column.name)
                    for column in model.__table__.columns
                } for item in data]
                
                self.number_of_rows = len(self.table_data)
                print(f"Found {len(self.table_data)} rows")
                # Calculate total pages
                self.total_pages = (self.number_of_rows + self.current_limit - 1) // self.current_limit
                
                # Initialize first page
                await self.paginate()

    async def paginate(self):
        start = self.offset
        end = start + self.current_limit
        
        # Serialize data before pagination
        serialized_data = []
        for row in self.table_data[start:end]:
            serialized_row = {}
            for key, value in row.items():
                if isinstance(value, dict):
                    # Convert dictionaries to formatted JSON string
                    serialized_row[key] = json.dumps(value, indent=2)
                elif isinstance(value, (datetime, timezone)):
                    # Convert datetime objects to ISO format
                    serialized_row[key] = value.isoformat()
                else:
                    # Convert everything else to string
                    serialized_row[key] = str(value) if value is not None else ""
            serialized_data.append(serialized_row)
            
        self.paginated_data = serialized_data
        self.current_page = (self.offset // self.current_limit) + 1

    async def delta_limit(self, limit: str):
        self.current_limit = int(limit)
        self.offset = 0
        self.total_pages = (
            self.number_of_rows + self.current_limit - 1
        ) // self.current_limit
        await self.paginate()

    async def previous(self):
        if self.offset >= self.current_limit:
            self.offset -= self.current_limit
        else:
            self.offset = 0

        await self.paginate()

    async def next(self):
        if self.offset + self.current_limit < self.number_of_rows:
            self.offset += self.current_limit

        await self.paginate()

    async def delta_drawer(self) -> None:
        """Toggle drawer state."""
        if self.is_open:
            await self.reset_state()
        else:
            await self.clear_error()
            self.is_open = True

    async def display_selected_row(self, data: Dict[str, Any]) -> None:
        """Display selected row in drawer."""
        if not data:
            await self.show_error_message("No data to display")
            return
            
        await self.clear_error()
        self.selected_entry = {k: v for k, v in data.copy().items() if k not in self.readonly_fields}
        self.original_entry = data.copy()
        await self.delta_drawer()

    @rx.event
    async def update_data(self, value: str, field_name: rx.Var) -> None:
        """Update a field in the selected entry.
        
        Args:
            value: New value for the field
            field_name: Name of the field to update
        """
        try:
            await self.clear_error()
            field_name_str = str(field_name)
            self.selected_entry[field_name_str] = str(value)
        except Exception as e:
            await self.show_error_message(f"Error updating {field_name_str}: {str(e)}")

    async def commit_changes(self) -> None:
        """Commit changes to the database."""
        with rx.session() as session:
            model = MODEL_FACTORY.get(self.current_table)
            if model:
                item = session.exec(
                    model.select().where(
                        model.id == self.original_entry["id"]
                    )
                ).first()
                if not item:
                    await self.show_error_message(f"No {self.current_table} found with id {self.selected_entry['id']}")
                    return
                # Update fields
                for key, value in self.selected_entry.items():
                    if hasattr(item, key) and key != 'id':
                        try:
                            if key == 'configuration':
                                converted_value = yaml.safe_load(value)
                            else:
                                converted_value = value
                            setattr(item, key, converted_value)
                        except Exception as e:
                            await self.show_error_message(f"Error updating {key}: {str(e)}")
                            return
                # Commit changes
                try:
                    item.last_updated = datetime.now().isoformat()
                    session.add(item)
                    session.commit()
                    session.refresh(item)
                    await self.clear_error()
                except Exception as e:
                    session.rollback()
                    await self.show_error_message(f"Error committing changes: {str(e)}")
                    return
        try:
            # Update local data while preserving unmodified fields
            self.table_data = [
                {**entry, **self.selected_entry} if entry["id"] == self.original_entry["id"] else entry 
                for entry in self.table_data
            ]
            await self.paginate()
            await self.reset_state()
            return rx.toast(
                "Changes saved successfully.",
                duration=3000,  # 3 seconds
                position="bottom-right",
                style={
                    "background-color": "rgba(0, 128, 0, 0.8)",  # Green with 0.8 opacity
                    "color": "white",
                    "border": "1px solid green",
                    "border-radius": "0.53m",
                }
            )
        except Exception as e:
            await self.show_error_message(f"Error updating local data: {str(e)}")
            return

