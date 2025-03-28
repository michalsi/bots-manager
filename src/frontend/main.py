import time
from datetime import datetime

import httpx
import pandas as pd
import streamlit as st

# Constants
API_BASE_URL = "http://backend:8000"  # Using docker service name
REFRESH_INTERVAL = 60  # seconds


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
        return pd.DataFrame(), {}

    # Store full bot data in a dictionary using a unique identifier
    bots_lookup = {bot['grid_id']: bot for bot in bots_data}

    # Select and rename columns for display
    columns_mapping = {
        'grid_id': 'Grid ID',
        'symbol': 'Symbol',
        'status': 'Status',
        'total_investment': 'Investment',
        'pnl': 'PnL',
        'pnl_percentage': 'PnL %',
        'current_price': 'Current Price',
        'mark_price': 'Mark Price',
        'total_apr': 'APR %',
        'running_duration': 'Duration (h)',
        'last_synced_at': 'Last Update'
    }
    df = pd.DataFrame(bots_data)
    df = df[columns_mapping.keys()].rename(columns=columns_mapping)
    # Format numeric columns
    df['Investment'] = df['Investment'].round(2)
    df['PnL'] = df['PnL'].round(2)
    df['PnL %'] = df['PnL %'].round(2)
    df['Current Price'] = df['Current Price'].round(4)
    df['Mark Price'] = df['Mark Price'].round(4)
    df['APR %'] = df['APR %'].round(2)
    df['Duration (h)'] = df['Duration (h)'].round(1)
    df['Last Update'] = df['Last Update'].apply(format_datetime)
    return df, bots_lookup


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
    # Fetch and display bots data
    with st.spinner("Loading bots data..."):
        bots_data = fetch_bots()
        df, bots_lookup = create_bots_dataframe(bots_data)

    if df.empty:
        st.warning("No bots data available")
    else:
        # Calculate summary metrics
        total_investment = df['Investment'].sum()
        total_pnl = df['PnL'].sum()
        total_pnl_percentage = (total_pnl / total_investment * 100) if total_investment else 0
        active_bots = len(df[df['Status'] == 'RUNNING'])
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Investment", f"${total_investment:,.2f}")
        col2.metric("Total PnL", f"${total_pnl:,.2f}")
        col3.metric("Total PnL %", f"{total_pnl_percentage:.2f}%")
        col4.metric("Active Bots", active_bots)

        df['Details'] = False  # Add a column for toggles
        display_columns = [col for col in df.columns if col != 'Grid ID']  # Exclude Grid ID from display

        column_config = {
            "PnL": st.column_config.NumberColumn(format="$%.2f"),
            "PnL %": st.column_config.NumberColumn(format="%.2f%%"),
            "APR %": st.column_config.NumberColumn(format="%.2f%%"),
            "Details": st.column_config.CheckboxColumn(
                "Show Details",
                help="Click to show detailed information"
            )
        }

        df['temp_index'] = range(len(df))
        display_df = df[display_columns].copy()
        display_df['temp_index'] = df['temp_index']

        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        complete_df = edited_df.merge(
            df[['temp_index', 'Grid ID']],
            on='temp_index',
            how='left'
        )
        for index, row in complete_df.iterrows():
            if row['Details']:
                with st.expander(f"Details for {row['Symbol']}", expanded=True):
                    bot_data = bots_lookup.get(row['Grid ID'])
                    if bot_data:
                        display_bot_details(bot_data)


if __name__ == "__main__":
    main()
