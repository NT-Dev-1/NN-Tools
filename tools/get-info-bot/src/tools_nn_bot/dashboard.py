"""Inline keyboard dashboard for Tools_NNBot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_main_dashboard() -> InlineKeyboardMarkup:
    """Create the main inline dashboard.

    Returns:
        InlineKeyboardMarkup with dashboard buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 System Status", callback_data="dashboard_system"),
            InlineKeyboardButton("🔌 Plugins", callback_data="dashboard_plugins"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="dashboard_help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="dashboard_settings"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="dashboard_refresh"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_plugins_dashboard() -> InlineKeyboardMarkup:
    """Create the plugins management dashboard.

    Returns:
        InlineKeyboardMarkup with plugin buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔗 Get Info", callback_data="plugin_info_getinfo"),
            InlineKeyboardButton("⚙️ System", callback_data="plugin_info_system"),
        ],
        [
            InlineKeyboardButton("« Back to Main", callback_data="dashboard_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_button() -> InlineKeyboardMarkup:
    """Create a simple back button.

    Returns:
        InlineKeyboardMarkup with back button
    """
    keyboard = [[InlineKeyboardButton("« Back", callback_data="dashboard_main")]]
    return InlineKeyboardMarkup(keyboard)
