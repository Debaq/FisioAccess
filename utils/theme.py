def set_theme(app):
    app.theme_cls.primary_palette = 'DeepPurple'
    app.theme_cls.theme_style = 'Light'  # Puedes cambiar a 'Dark' si prefieres el tema oscuro
    print(f"Theme set to {app.theme_cls.primary_palette} with style {app.theme_cls.theme_style}")
