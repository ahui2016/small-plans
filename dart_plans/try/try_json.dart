import 'dart:convert';

void main() {
  var todo = TodoItem.fromSummary('abc', 'def');
  print(todo);
  print(todo.runtimeType);
  var j = json.encode(todo);
  print(j);
  var item = TodoItem.fromJson(json.decode(j));
  print(item);
  print(item.runtimeType);
}

class TodoItem {
  String id, summary, details, tag;
  int createdAt, updatedAt, doneAt, deletedAt;

  TodoItem(this.id, this.summary, this.details, this.tag,
      this.createdAt, this.updatedAt, this.doneAt, this.deletedAt);

  TodoItem.fromSummary(this.summary, this.tag) {
    var now = DateTime.now().millisecondsSinceEpoch;
    id = now.toRadixString(36);
    details = ''; createdAt = now; updatedAt = now;
  }

  // 用于 json
  factory TodoItem.fromJson(dynamic j) => TodoItem(
      j['id'] as String, j['summary'] as String, j['details'] as String, j['tag'] as String,
      j['createdAt'] as int, j['updatedAt'] as int, j['doneAt'] as int, j['deletedAt'] as int);

  // 用于 json
  Map toJson() => { 'id': id,
    'summary': summary, 'details': details, 'tag': tag, 'createdAt': createdAt,
    'updatedAt': updatedAt, 'doneAt': doneAt, 'deletedAt': deletedAt,
  };
}