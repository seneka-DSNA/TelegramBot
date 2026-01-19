async def on_login_success(update, context):
    from handlers_menu import menu_handler
    await menu_handler(update, context)
