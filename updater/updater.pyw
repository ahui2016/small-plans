from appJar import gui

with gui("更新助手", "680x500", font={'size': 18}) as app:
    app.label("更新助手\nan updater for small-plans", colspan=2, sticky="w")
    app.label('请先选择文件, 然后点击"添加"按钮', colspan=4, sticky="ew")
    app.entry("选择文件", kind="open", row=2, column=1, colspan=2)
    app.button("添加", row=2, column=3, sticky="")
    app.separator(row=3, colspan=4, sticky="ew")
    app.listbox("files", row=4, column=1, colspan=2)
