import base64
import hashlib
import time
from datetime import datetime

import httpx
import pandas as pd
import streamlit as st

API_BASE_URL = "http://backend:8000"
REFRESH_INTERVAL = 60  # seconds


def shorten_grid_id(grid_id: str, length: int = 6) -> str:
    """Convert a long grid_id into a shorter human-readable string."""
    hash_object = hashlib.sha256(str(grid_id).encode())
    b64_hash = base64.b64encode(hash_object.digest()).decode('utf-8')
    short_id = ''.join(c for c in b64_hash if c.isalnum())[:length]
    return short_id


def fetch_bots():
    """Fetch bots data from the backend API"""
    with httpx.Client() as client:
        response = client.get(f"{API_BASE_URL}/bots/")
        response.raise_for_status()
        return response.json()


def format_datetime(dt_str):
    """Format datetime string to a more readable format"""
    if dt_str:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return ''


def format_duration(seconds: str) -> str:
    """Convert duration from seconds to 'XD Yh Zm' format"""
    try:
        seconds = int(float(seconds))
        days = seconds // (24 * 3600)
        seconds %= (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60

        if days > 0:
            return f"{days}D {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except (ValueError, TypeError):
        return "0m"

def get_compact_column_config():
    """Define compact column configuration with custom widths and multi-line headers"""
    return {
        "Bot ID": st.column_config.TextColumn(
            "Bot\nID",
            help="Shortened bot identifier",
            disabled=True,
            width="small"
        ),
        "Symbol": st.column_config.TextColumn(
            "Symbol",
            width="small"
        ),
        "Leverage": st.column_config.NumberColumn(
            "Lev",  # Shortened name
            help="Leverage",
            width="xs"
        ),
        "Investment": st.column_config.NumberColumn(
            "Invest\n($)",
            format="%.2f",
            width="small"
        ),
        "PnL": st.column_config.TextColumn(
            "PnL\n($)",
            width="xs"
        ),
        "PnL %": st.column_config.TextColumn(
            "PnL\n%",
            width="xs"
        ),
        "Current Price": st.column_config.NumberColumn(
            "Price\n($)",
            format="%.4f",
            width="small"
        ),
        "Duration (h)": st.column_config.TextColumn(
            "Run\nTime",
            help="Running duration in days, hours, and minutes",
            width="small"
        ),
        "Arbitrage Count": st.column_config.NumberColumn(
            "Arb\nCount",
            width="xs"
        ),
        "Details": st.column_config.CheckboxColumn(
            "Show\nDetails",
            help="Click to show detailed information",
            width="xs"
        )
    }

def update_bots():
    """Trigger bot data update from Bybit"""
    try:
        response = httpx.post(f"{API_BASE_URL}/bots/update")
        response.raise_for_status()
        st.success("Bots data successfully updated!")
        time.sleep(1)  # Give the backend time to process
        return True
    except httpx.HTTPStatusError as e:
        st.error(f"Failed to update bots data: {e}")


def create_bots_dataframe(bots_data):
    """Create a pandas DataFrame from bots data with selected columns"""
    if not bots_data:
        return pd.DataFrame(), {}, {}

    # Add short_id to each bot
    for bot in bots_data:
        bot['short_id'] = shorten_grid_id(bot['grid_id'])

    # Store full bot data in a dictionary using grid_id as key
    bots_lookup = {bot['grid_id']: bot for bot in bots_data}

    # Also create a lookup using short_id
    short_id_lookup = {bot['short_id']: bot['grid_id'] for bot in bots_data}

    # Select and rename columns for display
    columns_mapping = {
        'short_id': 'Bot ID',
        'grid_id': 'Original Grid ID',  # Keep for reference but will hide later
        'symbol': 'Symbol',
        'status': 'Status',
        'leverage': 'Leverage',
        'total_investment': 'Investment',
        'pnl': 'PnL',
        'pnl_percentage': 'PnL %',
        'current_price': 'Current Price',
        'running_duration': 'Duration (h)',
        'arbitrage_num': 'Arbitrage Count',
    }
    df = pd.DataFrame(bots_data)
    df = df[
        ['short_id', 'grid_id'] + [col for col in columns_mapping.keys() if col not in ['short_id', 'grid_id']]].rename(
        columns=columns_mapping)

    # Format numeric columns
    df['Investment'] = df['Investment'].round(2)
    df['Leverage'] = df['Leverage'].astype(int)

    # Store numeric PnL values before formatting
    df['PnL_numeric'] = df['PnL'].round(2)
    df['PnL %_numeric'] = df['PnL %'].round(2)

    # Format PnL values for display
    df['PnL'] = df['PnL_numeric'].apply(lambda x: f"{'🔴' if x < 0 else '🟢'} {x:.2f}")
    df['PnL %'] = df['PnL %_numeric'].apply(lambda x: f"{'🔴' if x < 0 else '🟢'} {x:.2f}%")

    df['Current Price'] = df['Current Price'].round(4)
    df['Duration (h)'] = df['Duration (h)'].apply(format_duration)
    df['Arbitrage Count'] = df['Arbitrage Count'].astype(int)
    return df, bots_lookup, short_id_lookup


def display_bot_details(bot_data):
    """Display detailed information for a single bot"""
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Bot Configuration**")
        st.write(f"Bot Type: {bot_data.get('bot_type', 'N/A')}")
        st.write(f"Grid Mode: {bot_data.get('grid_mode', 'N/A')}")
        st.write(f"Grid Type: {bot_data.get('grid_type', 'N/A')}")
        st.write(f"Leverage: {bot_data.get('leverage', 'N/A')}x")
        st.write(f"Number of Cells: {bot_data.get('cell_num', 'N/A')}")
    with col2:
        st.write("**Price Information**")
        st.write(f"Min Price: ${bot_data.get('min_price', 'N/A'):,.4f}")
        st.write(f"Max Price: ${bot_data.get('max_price', 'N/A'):,.4f}")
        st.write(f"Entry Price: ${bot_data.get('entry_price', 'N/A'):,.4f}")
        st.write(f"Liquidation Price: ${bot_data.get('liq_price', 'N/A'):,.4f}")
        st.write(f"Arbitrage Count: {bot_data.get('arbitrage_num', 'N/A')}")


def main():
    st.set_page_config(
        page_title="Trading Bots Dashboard",
        page_icon="📈",
        layout="wide"
    )
    st.title("Trading Bots Dashboard")
    # Add update button with loading state
    col1, col2 = st.columns([1, 11])
    with col1:
        if st.button("🔄 Update"):
            with st.spinner("Updating bots data..."):
                success = update_bots()
                if success:
                    st.rerun()

    with st.spinner("Loading bots data..."):
        bots_data = fetch_bots()
        df, bots_lookup, short_id_lookup = create_bots_dataframe(bots_data)

    if df.empty:
        st.warning("No bots data available")
    else:
        # Calculate summary metrics
        total_investment = df['Investment'].sum()
        # Use numeric PnL value for calculations
        total_pnl = df['PnL_numeric'].sum()
        total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        active_bots = len(df[df['Status'] == 'RUNNING'])

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Investment", f"${total_investment:,.2f}")
        col2.metric("Total PnL", f"${total_pnl:,.2f}")
        col3.metric("Total PnL %", f"{total_pnl_percentage:.2f}%")
        col4.metric("Active Bots", active_bots)

        df['Details'] = False  # Add a column for toggles

        # Instead of using excluded_columns, drop the column before display
        display_df = df.copy()
        display_df = display_df.drop(columns=["Original Grid ID"])
        display_df = display_df.drop(columns=["Status"])
        # Drop the numeric columns used for calculations
        display_df = display_df.drop(columns=["PnL_numeric", "PnL %_numeric"])

        column_config = {
            "Bot ID": st.column_config.TextColumn(
                "Bot ID",
                help="Shortened bot identifier",
                disabled=True
            ),
            "PnL": st.column_config.TextColumn("PnL"),  # Changed from NumberColumn to TextColumn
            "PnL %": st.column_config.TextColumn("PnL %"),  # Changed from NumberColumn to TextColumn
            "Duration (h)": st.column_config.TextColumn(
                "Duration",
                help="Running duration in days, hours, and minutes"
            ),
            "Details": st.column_config.CheckboxColumn(
                "Show Details",
                help="Click to show detailed information"
            )
        }
        column_config = get_compact_column_config()

        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )

        # Display detailed information for selected bots
        for index, row in edited_df.iterrows():
            if row['Details']:
                # Get the original grid_id using the short_id
                original_grid_id = df.at[index, 'Original Grid ID']

                with st.expander(f"Details for {row['Symbol']} (Bot ID: {row['Bot ID']})", expanded=True):
                    bot_data = bots_lookup.get(original_grid_id)
                    if bot_data:
                        display_bot_details(bot_data)


if __name__ == "__main__":
    main()
