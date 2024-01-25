grammar language;

BOOL: 'true' | 'false';
INT: '-'? [1-9][0-9]*;
VAR: [a-zA-Z_][a-zA-Z0-9_]*;
STRING: '"' ~[\n]* '"';
SPACES : [ \t\r]+ -> skip;

pattern: '_'
    | VAR
    | VAR (SPACES VAR)*
    ;

set: VAR
  | '{' expr (',' expr)* '}'
  | '{}'
  | 'get_start' '(' graph ')'
  | 'get_final' '(' graph ')'
  | 'get_reachable' '(' graph ')'
  | 'get_vertices' '(' graph ')'
  | 'get_edges' '(' graph ')'
  | 'get_labels' '(' graph ')'
  | 'map' '((' 'fun' pattern '->' expr ')' ',' set ')'
  | 'filter' '((' 'fun' pattern '->' expr ')' ',' set ')'
  | '(' set ')'
  ;

graph: VAR
  | 'set_start' '(' set ',' graph ')'
  | 'set_final' '(' set ',' graph ')'
  | 'add_start' '(' (INT | STRING) ',' graph ')'
  | 'add_final' '(' (INT | STRING) ',' graph ')'
  | 'load_from_file' '(' STRING ')'
  | 'load_from_name' '(' STRING ')'
  ;

regex: 'r' STRING;

val: INT
  | BOOL
  | STRING
  | graph
  | set
  | regex
  ;

lang_binops: 'intersect' | 'union' | 'concat';
bool_binops: '&&' | '||' | 'in';

expr: VAR
  | val
  | expr lang_binops expr
  | expr bool_binops expr
  | '-' expr
  | 'not' expr
  | expr '*'
  | '(' expr ')'
  ;

stmt: VAR '=' expr
  | 'print' expr
  ;

EOL: '\n';

prog: EOL* stmt (EOL+ stmt)* EOL* EOF;
