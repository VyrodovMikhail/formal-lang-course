## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val = Bool of bool
  | String of string
  | Int of int
  | Graph of graph // nx.MultiDiGraph
  | Regex of regex // pyformlang.Regex

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda = var * expr
```

## Конкретная грамматика

```
prog = (statement '\n')*

statement ->
    | VAR '=' expr
    | 'print' expr

expr ->
    '(' expr ')'
  | VAR
  | val
  | intersect
  | concat
  | union
  | star
  | contains

set -> var
  | '{' expr (',' expr)* '}'
  | 'set()'
  | 'get_start' '(' graph ')'
  | 'get_final' '(' graph ')'
  | 'get_reachable' '(' graph ')'
  | 'get_vertices' '(' graph ')'
  | 'get_edges' '(' graph ')'
  | 'get_labels' '(' graph ')'
  | 'map' '(' 'fun' VAR '->' expr ')'
  | 'filter' '(' 'fun' VAR '->' expr ')'
  | '(' set ')'

val -> STRING
  | INT
  | BOOL
  | graph
  | regex
  | set

regex -> 'r' STRING

graph -> var
  | 'graph' STRING
  | 'set_start' '(' set ',' graph ')'
  | 'set_final' '(' set ',' graph ')'
  | 'add_start' '(' (INT | STRING) ',' graph ')'
  | 'add_final' '(' (INT | STRING) ',' graph ')'
  | 'load_from_file' STRING
  | 'load_from_name' STRING

intersect -> 'intersect' '(' expr ',' expr ')'
concat -> 'concat' '(' expr ',' expr ')'
union -> 'union' '(' expr ',' expr ')'
star -> '(' expr ')' '*'
contains -> expr 'in' set

BOOL --> 'true' | 'false'
INT -> '-'? [1-9][0-9]*
VAR -> [a-zA-Z_][a-zA-Z0-9_]*
STRING -> '"' ~[\n]* '"'
```

## Примеры программ на языке

Загрузка графа и проверка принадлежности числа к вершинам графа
```
my_graph = load_from_file("./filename")
vertices_set = get_vertices(graph)
contains_flag = contains(5, vertices_set)
print contains_flag
```

Простые операции над графом
```
first_graph = load_from_file("./filename")
first_graph = add_start("A", my_graph)
second_graph = load_from_file("./filename2")
intersect_graph = intersect(first_graph, second_graph)
intersection_labels = get_labels(intersection_graph)
print intersection_labels
```

Пересечение с регулярным выражением
```
my_graph = load_from_file("./filename")
my_regex = r"a | b"
intersection = intersect(my_graph, my_regex)
reachable_vertices = get_reachable(intersection)
print reachable_vertices
```

Операции с лямбдами
```
my_graph = load_from_file("./filename")
vertices = get_vertices(my_graph)
filtered_vertices = filter((fun x -> x in {"A", "B"}), vertices)
print filtered_vertices
```
