import 'dart:async';
import 'dart:convert';
import 'dart:html';

final String localLocation = Uri.decodeFull(window.location.toString());
final String workingDir = makeWorkingDir(localLocation);
final String prefix = makePrefix(localLocation);
final String projectTitleKey = '${prefix}projectTitle';
final String descriptionKey = '${prefix}projectDescription';

Element browserTabTitle = querySelector('title');
Element projectTitleSection = querySelector('#proj-title-section');
Element projectTitle = querySelector('#project-title');
Element projectDescription = querySelector('#proj-description');
Element projectTitleDialog = querySelector('#proj-title-dialog');
InputElement projectTitleInput = querySelector('#proj-title-input');
TextAreaElement descriptionInput = querySelector('#description-input');

Element exportImportButtons = querySelector('#export-import-buttons');
Element importDialog = querySelector('#import-dialog');
InputElement importDir = querySelector('#import-dir');
Element exportDialog = querySelector('#export-dialog');
InputElement exportDir = querySelector('#export-dir');

InputElement todoInput = querySelector('#todo-input');
TemplateElement todoTemplate = querySelector('#todo-template');

List<TodoItem> undoneItems = [];
Element undoneElements = querySelector('#undone-elements');
List<TodoItem> doneItems = [];
Element doneElements = querySelector('#done-elements');
List<TodoItem> deletedItems = [];
Element deletedElements = querySelector('#deleted-elements');

// 为了便于检索 todoitem.
List<TodoItem> allItems = [];

class TodoItem {
  String id, summary, details, tag;
  DateTime createdAt, updatedAt, doneAt, deletedAt;

  TodoItem(this.id, this.summary, this.details, this.tag,
      this.createdAt, this.updatedAt, this.doneAt, this.deletedAt);

  TodoItem.fromSummary(this.summary, this.tag) {
    var now = DateTime.now();
    id = now.millisecondsSinceEpoch.toRadixString(36);
    details = ''; createdAt = now; updatedAt = now;
    // doneAt = null, deletedAt = null
  }

  // 用于 json
  factory TodoItem.fromJson(dynamic j) => TodoItem(
      j['id'] as String, j['summary'] as String, j['details'] as String, j['tag'] as String,
      DateTime.fromMillisecondsSinceEpoch(j['createdAt']),
      DateTime.fromMillisecondsSinceEpoch(j['updatedAt']),
      (j['doneAt'] == null) ? null : DateTime.fromMillisecondsSinceEpoch(j['doneAt']),
      (j['deletedAt'] == null) ? null : DateTime.fromMillisecondsSinceEpoch(j['deletedAt']));

  // 用于 json
  Map toJson() => { 'id': id, 'summary': summary, 'details': details, 'tag': tag,
    'createdAt': createdAt.millisecondsSinceEpoch,
    'updatedAt': updatedAt.millisecondsSinceEpoch,
    'doneAt': doneAt?.millisecondsSinceEpoch,
    'deletedAt': deletedAt?.millisecondsSinceEpoch,
  };
}

void main() {
  init();
  todoInput.focus();
  window.console.log(prefix);
}

/// 初始化一些东西, 比如给一些按钮添加事件.
void init() {
  initTitleDescription();
  initExportDialog();
  initImportDialog();
  initAddTodoForm();
  restoreTodos();
  initAllDetailsButtons();
}

/// 注意每当修改 `window.localStorage[projectTitleKey]` 的时候, 都要避免其值为空字符串,
/// 如果其值为空字符串, 则自动设为 'Small Plans'.
void initTitleDescription() {
  window.localStorage[projectTitleKey] ??= 'Small Plans';
  projectTitle.text = window.localStorage[projectTitleKey];
  browserTabTitle.text = projectTitle.text;
  projectDescription.text = window.localStorage[descriptionKey];

  querySelector('#proj-title-btn').onClick.listen((_) {
    projectTitleInput.value = window.localStorage[projectTitleKey];
    descriptionInput.value = window.localStorage[descriptionKey];
    projectTitleSection.setAttribute('hidden', '');
    projectTitleDialog.removeAttribute('hidden');
    projectTitleInput.focus();
  });

  querySelector('#proj-title-cancel').onClick.listen((e) {
    e.preventDefault();
    projectTitleSection.removeAttribute('hidden');
    projectTitleDialog.setAttribute('hidden', '');
  });

  querySelector('#proj-title-ok').onClick.listen((e) {
    e.preventDefault();
    projectTitle.text = projectTitleInput.value.trim();
    if (projectTitle.text.isEmpty) projectTitle.text = 'Small Plans';
    window.localStorage[projectTitleKey] = projectTitle.text;
    browserTabTitle.text = projectTitle.text;
    projectDescription.text = descriptionInput.value.trim();
    window.localStorage[descriptionKey] = projectDescription.text;
    projectTitleSection.removeAttribute('hidden');
    projectTitleDialog.setAttribute('hidden', '');
  });
}

void restoreTodos() {
  window.localStorage.forEach((k, v) {
    if (k.startsWith(prefix) && k != projectTitleKey && k != descriptionKey) {
      var todoitem = TodoItem.fromJson(json.decode(v));
      if (todoitem.deletedAt != null) {
        deletedItems.add(todoitem);
      } else if (todoitem.doneAt != null) {
        doneItems.add(todoitem);
      } else {
        undoneItems.add(todoitem);
      }
      allItems.add(todoitem);
    }
  });
  undoneItems
    ..sort((a, b) => a.createdAt.compareTo(b.createdAt))
    ..forEach(insertTodoElement);
  doneItems
    ..sort((a, b) => a.doneAt.compareTo(b.doneAt))
    ..forEach(insertTodoElement);
  deletedItems
    ..sort((a, b) => a.deletedAt.compareTo(b.deletedAt))
    ..forEach(insertTodoElement);
}

void initExportDialog() {
  querySelector('#export-button').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.setAttribute('hidden', '');
    exportDialog.removeAttribute('hidden');
  });

  exportDir.value = workingDir;

  querySelector('#export-copy-btn').onClick.listen((e) {
    e.preventDefault();

    Future(() {
      exportDir.select();
    }).then((_) {
      window.document.execCommand('copy');
    });
  });

  querySelector('#export-dialog-close').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.removeAttribute('hidden');
    exportDialog.setAttribute('hidden', '');
  });
}

void initImportDialog() {
  querySelector('#import-button').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.setAttribute('hidden', '');
    importDialog.removeAttribute('hidden');
  });

  importDir.value = workingDir;

  querySelector('#import-copy-btn').onClick.listen((e) {
    e.preventDefault();

    Future(() {
      importDir.select();
    }).then((_) {
      window.document.execCommand('copy');
    });
  });

  querySelector('#import-dialog-close').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.removeAttribute('hidden');
    importDialog.setAttribute('hidden', '');
  });
}

void initAddTodoForm() =>
    querySelector('#add-todo-form').onSubmit.listen((e) {
      e.preventDefault();
      var todo = todoInput.value.trim();
      if (todo.isEmpty) return;
      var tagSummary = splitTagSummary(todo);
      var item = TodoItem.fromSummary(tagSummary['summary'], tagSummary['tag']);
      updateLocalStorage(item);
      allItems.add(item);
      undoneItems.add(item);
      insertTodoElement(item);
      todoInput.value = '';
      todoInput.focus();
    });

// 注意: 每当修改 todoitem 的内容时, 都要更新 localStorage.
void insertTodoElement(TodoItem todoitem) {
  DocumentFragment todoNode = todoTemplate.content.clone(true);
  var todoElement = todoNode.querySelector('.todo-element');
  todoElement.setAttribute('id', todoitem.id);

  var todoTag = todoElement.querySelector('.todo-tag');
  todoTag.text = todoitem.tag;

  var todoSummary = todoElement.querySelector('.todo-summary');
  todoSummary.text = todoitem.summary;

  var todoDetails = todoElement.querySelector('.todo-details');
  todoDetails.text = todoitem.details;

  initMoreButton(todoitem, todoElement, todoDetails);
  initDetailsButtons(todoitem, todoElement);

  if (todoitem.deletedAt != null) {
    setDeletedAttributes(todoitem, todoElement);
    deletedElements.insertBefore(todoNode, deletedElements.firstChild);
  } else if (todoitem.doneAt != null) {
    setDoneAttributes(todoitem, todoElement);
    doneElements.insertBefore(todoNode, doneElements.firstChild);
  } else {
    setUndoneAttributes(todoElement);
    undoneElements.insertBefore(todoNode, undoneElements.firstChild);
  }
}

void initMoreButton(TodoItem todoitem, Element todoElement, Element todoDetails) {
  var moreButton = todoElement.querySelector('.more-btn');
  var summaryNode = todoElement.querySelector('summary');
  var detailsNode = todoElement.querySelector('details');

  if (todoitem.details.isNotEmpty) moreButton.removeAttribute('hidden');

  summaryNode.onClick.listen((_) {
    if (detailsNode.hasAttribute('open') && todoDetails.text.trim().isNotEmpty) {
      moreButton.removeAttribute('hidden');
    } else {
      moreButton.setAttribute('hidden', '');
    }
  });
}

void initAllDetailsButtons() {
  for (var todo in querySelectorAll('.todo-element')) {
    var id = todo.getAttribute('id');
    var todoitem = allItems.firstWhere((item) => item.id == id);
    initDetailsButtons(todoitem, todo);
  }
}

void initDetailsButtons(TodoItem todoitem, Element todo) {
    initDoneButton(todoitem, todo);
    initUndoneButton(todoitem, todo);
    initDeleteButton(todoitem, todo);
    initRestoreButton(todoitem, todo);
    initDeleteForeverButton(todoitem, todo);
    initTodoEditButton(todoitem, todo);
    initTodoEditCancel(todo);
    initTodoEditOk(todoitem, todo);
}

void initDoneButton(TodoItem todoitem, Element todo) =>
    todo.querySelector('.doneBtn').onClick.listen((_) {
      todoitem.doneAt = DateTime.now();
      if (todoitem.tag == 'bug') {
        todoitem.tag = 'fixed';
        todo.querySelector('.todo-tag').text = 'fixed';
      }
      updateLocalStorage(todoitem);
      doneItems.add(todoitem);
      undoneItems.remove(todoitem);
      setDoneAttributes(todoitem, todo);
      if (todoitem.details.isEmpty) {
        todo.querySelector('details').removeAttribute('open');
      }
      doneElements.insertBefore(todo, doneElements.firstChild);
    });

void setDoneAttributes(TodoItem todoitem, Element todo) {
  todo.querySelector('details').setAttribute('class', 'done');
  todo.querySelector('.done-at')
    ..removeAttribute('hidden')
    ..text = 'done at: ${simpleDate(todoitem.doneAt)}';
  todo.querySelector('.undoneBtn').removeAttribute('hidden');
  todo.querySelector('.doneBtn').setAttribute('hidden', '');
}

void initUndoneButton(TodoItem todoitem, Element todo) =>
    todo.querySelector('.undoneBtn').onClick.listen((_) {
      todoitem.doneAt = null;
      if (todoitem.tag == 'fixed') {
        todoitem.tag = 'bug';
        todo.querySelector('.todo-tag').text = 'bug';
      }
      updateLocalStorage(todoitem);
      undoneItems.add(todoitem);
      doneItems.remove(todoitem);
      setUndoneAttributes(todo);
      if (todoitem.details.isEmpty) {
        todo.querySelector('details').removeAttribute('open');
      }
      undoneElements.insertBefore(todo, undoneElements.firstChild);
    });

void setUndoneAttributes(Element todo) {
  todo.querySelector('details').setAttribute('class', 'undone');
  todo.querySelector('.done-at')
    ..setAttribute('hidden', '')
    ..text = '';
  todo.querySelector('.undoneBtn').setAttribute('hidden', '');
  todo.querySelector('.doneBtn').removeAttribute('hidden');
}

void initDeleteButton(TodoItem todoitem, Element todo) =>
    todo.querySelector('.deleteBtn').onClick.listen((_) {
      todoitem.doneAt = null;
      todoitem.deletedAt = DateTime.now();
      updateLocalStorage(todoitem);
      deletedItems.add(todoitem);
      undoneItems.remove(todoitem);
      doneItems.remove(todoitem);
      setDeletedAttributes(todoitem, todo);
      if (todoitem.details.isEmpty) {
        todo.querySelector('details').removeAttribute('open');
      }
      deletedElements.insertBefore(todo, deletedElements.firstChild);
    });

void setDeletedAttributes(TodoItem todoitem, Element todo) {
  todo.querySelector('details').setAttribute('class', 'deleted');
  todo.querySelector('.todo-summary').style.textDecoration = 'line-through';
  todo.querySelector('.done-at')..setAttribute('hidden', '')..text = '';
  todo.querySelector('.deleted-at')..removeAttribute('hidden')
    ..text = 'deleted at: ${simpleDate(todoitem.deletedAt)}';
  todo.querySelector('.undoneBtn').setAttribute('hidden', '');
  todo.querySelector('.doneBtn').setAttribute('hidden', '');
  todo.querySelector('.cell.buttons.normal').setAttribute('hidden', '');
  todo.querySelector('.cell.buttons.deleted').removeAttribute('hidden');
}

void initRestoreButton(TodoItem todoitem, Element todo) {
  var restoreButton = todo.querySelector('.restoreBtn');
  var details = todo.querySelector('details');

  restoreButton.onClick.listen((_) {
    todoitem.createdAt = DateTime.now();
    todoitem.deletedAt = null;
    if (todoitem.tag == 'fixed') {
      todoitem.tag = 'bug';
      todo.querySelector('.todo-tag').text = 'bug';
    }
    updateLocalStorage(todoitem);
    undoneItems.add(todoitem);
    deletedItems.remove(todoitem);
    setRestoreAttributes(todo);
    if (todoitem.details.isEmpty) details.removeAttribute('open');
    undoneElements.insertBefore(todo, undoneElements.firstChild);
  });
}

void setRestoreAttributes(Element todo) {
  todo.querySelector('details').setAttribute('class', 'undone');
  todo.querySelector('.todo-summary').style.textDecoration = '';
  todo.querySelector('.deleted-at')..setAttribute('hidden', '')..text = '';
  todo.querySelector('.doneBtn').removeAttribute('hidden');
  todo.querySelector('.cell.buttons.normal').removeAttribute('hidden');
  todo.querySelector('.cell.buttons.deleted').setAttribute('hidden', '');
}

void initDeleteForeverButton(TodoItem todoitem, Element todo) =>
    todo.querySelector('.deleteForeverBtn').onClick.listen((_) {
      deletedItems.remove(todoitem);
      allItems.remove(todoitem);
      window.localStorage.remove(localId(todoitem.id));
      todo.remove();
    });

void initTodoEditButton(TodoItem todoitem, Element todo) =>
    todo.querySelector('.editBtn').onClick.listen((_) {
      todo.querySelector('.dialog.todo-edit').removeAttribute('hidden');
      (todo.querySelector('.todo-summary-input') as InputElement).value = todoitem.summary;
      (todo.querySelector('.todo-details-input') as TextAreaElement).value = todoitem.details;
      (todo.querySelector('.todo-tag-input') as InputElement)
        ..value = todoitem.tag
        ..focus();
    });

void initTodoEditCancel(Element todo) =>
    todo.querySelector('.todo-edit-cancel').onClick.listen((e) {
      e.preventDefault();
      todo.querySelector('.dialog.todo-edit').setAttribute('hidden', '');
    });

void initTodoEditOk(TodoItem todoitem, Element todo) =>
    todo.querySelector('.todo-edit-ok').onClick.listen((e) {
      e.preventDefault();
      var tag = (todo.querySelector('.todo-tag-input') as InputElement).value.trim();
      var summary = (todo.querySelector('.todo-summary-input') as InputElement).value.trim();
      var details = (todo.querySelector('.todo-details-input') as TextAreaElement).value.trimRight();
      if (tag != todoitem.tag || summary != todoitem.summary || details != todoitem.details) {
        todoitem.tag = tag;
        todoitem.summary = summary;
        todoitem.details = details;
        todoitem.updatedAt = DateTime.now();
        todo.querySelector('.todo-tag').text = tag;
        todo.querySelector('.todo-summary').text = summary;
        todo.querySelector('.todo-details').text = details;
        updateLocalStorage(todoitem);
      }
      todo.querySelector('.dialog.todo-edit').setAttribute('hidden', '');
    });

/*
List<TodoItem> todoitemGroup(String group) {
  switch (group) {
    case 'undone': return undoneItems;
    case 'done': return doneItems;
    case 'deleted': return deletedItems;
    default: throw 'The group should be "undone", "done" or "deleted"';
  }
}
 */

// 返回格式为 '2020-03-23' 的字符串.
// 如果改写为 JavaScript 要注意时区问题.
String simpleDate(DateTime dt) => dt.toIso8601String().substring(0, 10);

String localId(String id) => '$prefix$id';

Map<String, String> splitTagSummary(String todo) {
  String tag, summary;
  if (todo.startsWith('#')) {
    var i = todo.indexOf('#', 1);
    if (i != -1) {
      tag = todo.substring(1, i).trim();
      summary = todo.substring(i + 1).trim();
    }
    return {'tag': tag, 'summary': summary};
  }
  return {'tag': '', 'summary': todo};
}

String makePrefix(String localPath) {
  var re = RegExp(r'[/\\:]'); // '/', '\' and ':'
  var prefix = localPath.replaceAll(re, '');
  prefix = prefix.substring('fileC'.length, prefix.length - '.html'.length);
  var len = prefix.length;
  if (len > 40) {
    // 取该字符串的头和尾组成 prefix (为了尽可能避免重复, 又不能太长)
    // 共 40 个字符, 相当于 SHA-1 长度.
    // 本来是计算 SHA-1 的, 但为了与旧版 (JavaScript版本) 保持一致.
    prefix = prefix.substring(0, 20) + prefix.substring(len - 20);
  }
  return '$prefix-'; // 注意 prefix 末尾有横杠.
}

String makeWorkingDir(String localPath) {
  var i = localPath.lastIndexOf('/');
  var workingDir = localPath.substring('file:///'.length, i + 1);
  if (window.navigator.platform.startsWith('Win')) {
    return workingDir.replaceAll(r'/', r'\');
  }
  return workingDir;
}

void updateLocalStorage(TodoItem todoitem) {
  window.localStorage[localId(todoitem.id)] = json.encode(todoitem);
}
