import 'dart:async';
import 'dart:html';
import 'dart:convert';

final String localLocation = Uri.decodeFull(window.location.toString());
final String workingDir = makeWorkingDir(localLocation);
final String prefix = makePrefix(localLocation);
final String projectTitleKey = '$prefix-projectTitle';
final String descriptionKey = '$prefix-projectDescription';

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
List<TodoItem> deletedItems = [];

class TodoItem {
  String id, summary, details, tag;
  int createdAt, updatedAt, doneAt, deletedAt;

  TodoItem(this.id, this.summary, this.details, this.tag,
      this.createdAt, this.updatedAt, this.doneAt, this.deletedAt);

  TodoItem.fromSummary(this.summary, this.tag) {
    var now = DateTime.now().millisecondsSinceEpoch;
    id = localId(now.toRadixString(36));
    details = ''; createdAt = now; updatedAt = now;
  }

  // 用于 json
  factory TodoItem.fromJson(dynamic j) {
    var _doneAt = j['doneAt'] ?? 0;
    var _deletedAt = j['deletedAt'] ?? 0;
    return TodoItem(
        j['id'] as String, j['summary'] as String, j['details'] as String, j['tag'] as String,
        j['createdAt'] as int, j['updatedAt'] as int, _doneAt as int, _deletedAt as int);
  }

  // 用于 json
  Map toJson() => { 'id': id,
    'summary': summary, 'details': details, 'tag': tag, 'createdAt': createdAt,
    'updatedAt': updatedAt, 'doneAt': doneAt, 'deletedAt': deletedAt,
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
      if (todoitem.deletedAt > 0) {
        deletedItems.add(todoitem);
      } else if (todoitem.doneAt > 0) {
        doneItems.add(todoitem);
      } else {
        undoneItems.add(todoitem);
      }
    }
  });
  undoneItems
    ..sort((a, b) => a.createdAt - b.createdAt)
    ..forEach(insertTodoElement);
  doneItems
    ..sort((a, b) => a.doneAt - b.doneAt)
    ..forEach(insertTodoElement);
  deletedItems
    ..sort((a, b) => a.deletedAt - b.deletedAt)
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

void initAddTodoForm() {
  querySelector('#add-todo-form').onSubmit.listen((e) {
    e.preventDefault();
    var todo = todoInput.value.trim();
    if (todo.isEmpty) return;
    var tagSummary = splitTagSummary(todo);
    var item = TodoItem.fromSummary(tagSummary['summary'], tagSummary['tag']);
    window.localStorage[localId(item.id)] = json.encode(item);
    undoneItems.add(item);
    insertTodoElement(item);
    todoInput.value = '';
    todoInput.focus();
  });
}

// 注意: 每当修改 todoitem 的内容时, 都要更新 localStorage.
void insertTodoElement(TodoItem todoitem) {
  DocumentFragment todoNode = todoTemplate.content.clone(true);
  var todoTopDiv = todoNode.querySelector('.todo-top-div');
  todoTopDiv.setAttribute('id', todoitem.id);

  var moreButton = todoTopDiv.querySelector('.more-btn');
  if (todoitem.details.isNotEmpty) moreButton.removeAttribute('hidden');

  var todoTag = todoTopDiv.querySelector('.todo-tag');
  todoTag.text = todoitem.tag;

  var todoSummary = todoTopDiv.querySelector('.todo-summary');
  todoSummary.text = todoitem.summary;

  var todoDetails = todoTopDiv.querySelector('.todo-details');
  todoDetails.text = todoitem.details;

  var summaryNode = todoTopDiv.querySelector('summary');
  var detailsNode = todoTopDiv.querySelector('details');
  summaryNode.onClick.listen((e) {
    if (detailsNode.hasAttribute('open') && todoDetails.text.trim().isNotEmpty) {
      moreButton.removeAttribute('hidden');
    } else {
      moreButton.setAttribute('hidden', '');
    }
  });

  undoneElements.insertBefore(todoNode, undoneElements.firstChild);
//  undoneElements.append(todoNode);
}

// 返回格式为 '2020-03-23' 的字符串.
// 如果改写为 JavaScript 要注意时区问题.
String simpleDate(int timestamp) =>
    DateTime
      .fromMillisecondsSinceEpoch(timestamp)
      .toIso8601String()
      .substring(0, 10);

String localId(String id) => '$prefix-$id';

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
  return prefix;
}

String makeWorkingDir(String localPath) {
  var i = localPath.lastIndexOf('/');
  var workingDir = localPath.substring('file:///'.length, i + 1);
  if (window.navigator.platform.startsWith('Win')) {
    return workingDir.replaceAll(r'/', r'\');
  }
  return workingDir;
}
