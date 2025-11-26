// GRAMATICA ALGORITMIA

grammar Algoritmia;

root: procDef* EOF;

inss: ins*;
ins: (condition | while_)
    | (read | write | proc | assign | reprod)
    | (listadd | listrem | looksheet) ;

read: '<?>' VAR;     
write: '<w>' expr+;  
condition: 'if' expr LB inss RB ('else' LB inss RB)?;
while_: 'while' expr LB inss RB;

siz: SIZE VAR;

NOTA: [A-G][0-9]?;

PROCNAME: [A-Z][a-zA-Z0-9_]*;
procDef: PROCNAME paramsId  LB inss RB;
proc: PROCNAME paramsExpr (expr)*;

assign: VAR ASSIGN expr;

looksheet: LOOK;
LOOK: 'look';

paramsId: (VAR)*;
paramsExpr: (expr)*;

reprod: REPROD expr;

listrem: LIST_REM VAR LS expr RS;
listadd: VAR LIST_ADD expr;

consult: VAR LS expr RS;

lista : '{' expr* '}';

// Expresiones

expr: expr MULT expr            # Mult
    | expr DIV expr             # Div
    | expr MOD expr             # Mod
    | expr PLUS expr            # Suma
    | expr MIN expr             # Min
    | expr GT expr              # Gt
    | expr GTE expr             # Gte
    | expr LT expr              # Lt
    | expr LTE expr             # Lte
    | expr EQ expr              # Eq
    | expr NEQ expr             # Neq
    | VAR                       # Var
    | STRING                    # String
    | NUM                       # Num
    | lista                     # List_
    | siz                       # Tamanio
    | consult                   # Consult_   
    | NOTA                      # Nota
    | LP expr RP                # Parens
    ;
    
// Tokens

VAR               : [a-zA-Z][a-zA-Z0-9]*;
NUM               : '-'?[0-9]+('.'[0-9]+)?;
STRING            : '"' ( '\\' . | ~('\\'|'"'))* '"';    
    
// Símbolos de agrupación    
    
LB                : '|:';
RB                : ':|';
LP                : '(';
RP                : ')';
LC                : '{';
RC                : '}';
LS                : '[';
RS                : ']';    
    
// Operadores   

PLUS              : '+';
MIN               : '-';
MULT              : '*';
DIV               : '/';
MOD               : '%';
EQ                : '=';
NEQ               : '/=';
GT                : '>';
LT                : '<';
GTE               : '>=';
LTE               : '<=';
LIST_REM          : '8<';    // Remover elemento de lista
LIST_ADD          : '<<';    // Añadir elemento a lista
ASSIGN            : '<-';    // Asignación de variable
REPROD            : '<:>';   // Reproducción de nota musical
SIZE              : '#';     // Tamaño de variable

// Comentarios y espacios en blanco
COMMENT           : '###' ~[\r\n]* -> skip;
WS                : [ \t\r\n]+ -> skip;



