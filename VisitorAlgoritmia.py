# VisitorAlgoritmia.py
import operator
import os
from collections import defaultdict
ops = {'+': operator.add, '-': operator.sub, '*': operator.mul,
       '/': operator.truediv, '^': operator.pow}

if __name__ is not None and "." in __name__:
    from .AlgoritmiaParser import AlgoritmiaParser
    from .AlgoritmiaVisitor import AlgoritmiaVisitor
else:
    from AlgoritmiaParser import AlgoritmiaParser
    from AlgoritmiaVisitor import AlgoritmiaVisitor


class AlgoritmiaException(Exception):
        def __init__(self, message):
            self.message = 'Error: ' + message


class Proceso:
    def __init__(self, name, params, inss):
        self.name = name
        self.params = params
        self.inss = inss

class Visitor(AlgoritmiaVisitor):
    
    def __init__(self, entryProc='Main', entryParams=None):
        if entryParams is None:
            entryParams = []
        
        self.entryProc = entryProc
        self.entryParams = entryParams
        
        self.procs = {}
        self.stack = []
        self.parti = []
        

        all_notes = [
            "A0", "B0", "C1", "D1", "E1", "F1", "G1", "A1", "B1", "C2", "D2", "E2", "F2", "G2",
            "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4",
            "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "E6", "F6", "G6",
            "A6", "B6", "C7", "D7", "E7", "F7", "G7", "A7", "B7", "C8"
        ]
        self.notes = {note: index for index, note in enumerate(all_notes)}
        self.adins= False

        
        
    def __proc__(self, name, paramsValues):
        expected_params = self.procs[name].params
        given_param_count = len(paramsValues)

        if len(expected_params) != given_param_count:
            expected_param_count = len(expected_params)
            raise AlgoritmiaException(f'En "{name}" proc se esperaba {expected_param_count} '
                                    f'param(s), {given_param_count} param(s) dados.')

        new_scope = defaultdict(lambda: 0)
        for param, value in zip(expected_params, paramsValues):
            new_scope[param] = value

        self.stack.append(new_scope)
        self.visit(self.procs[name].inss)

        self.stack.pop()
        
        
    def visitRoot(self, ctx):
        for proc in list(ctx.getChildren()):
            self.visit(proc)
            
        self.__proc__(self.entryProc, self.entryParams)

        if self.parti:
            # Genera el archivo lilypond y lo convierte a archivo de audio
            # Code to generate the LilyPond file and convert it to audio files only runs if there are notes.
            absolute_path = os.path.dirname(os.path.abspath(__file__))
            notes_partituraMajuscules = ' '.join(map(str, self.parti))
            notes = notes_partituraMajuscules.lower()
        
        # Contenido Lilypond
            lilypond_content = "\\version \"2.22.1\"\n" \
                            "\\score {\n" \
                            "\t \\absolute {\n" \
                            f"\t\t\\tempo 4 = 120\n{notes}\n" \
                            "\t }\n" \
                            "\t \\layout { }\n" \
                            "\t \\midi { }\n" \
                            "}"
        
            with open(os.path.join(absolute_path, "music.ly"), "w") as file:
                file.write(lilypond_content)

            # Lilypond genera el archivo midi
            os.system('lilypond music.ly')

            # Pasar de midi a wav con Timidity
            os.system('timidity -Ow -o music.wav music.midi')

            # Pasar de wav a pm3 con ffmpeg
            os.system('ffmpeg -i music.wav -codec:a libmp3lame -qscale:a 2 music.mp3')
     
    
    def visitGte(self, ctx):
        left_node = ctx.getChild(0)
        right_node = ctx.getChild(1)
        left_value = self.notes.get(left_node.getText(), self.visit(left_node))
        right_value = self.notes.get(right_node.getText(), self.visit(right_node))
        return int(left_value >= right_value)
        
    
    def visitMod(self, ctx):
        return self.visit(ctx.getChild(0)) % self.visit(ctx.getChild(2))    

    def visitParamsId(self,ctx):
        lista = []
        for p in list(ctx.getChildren()):
            lista.append(p.getText())
        
        return lista
    
            
    def visitParamsExpr(self, ctx):
        return [self.visit(child) for child in ctx.getChildren()]    
    
    
    def visitWrite(self, ctx):
        output_elements = []
        children = list(ctx.getChildren())[1:]  # Skip the 'write' keyword

        for child in children:
            result = self.visit(child)
            if isinstance(result, list):
                # Convert list elements to strings and join them with spaces
                output_elements.append(' '.join(map(str, result)))
            else:
                output_elements.append(str(result))
        print(' '.join(output_elements))
                
    def visitInss(self,ctx):
        for ins in list(ctx.getChildren()):
            self.visit(ins)
            

    def visitRead(self, ctx):
        variable_name = ctx.getChild(1).getText()
        self.stack[-1][variable_name] = int(input(f"Introduce la variable {variable_name}: "))    
    
    def visitEq(self, ctx):
        left_value = self.get_value_or_note_value(ctx.getChild(0))
        right_value = self.get_value_or_note_value(ctx.getChild(1))
        return int(left_value == right_value)    
    
    def visitReprod(self, ctx):
        notes = self.visit(ctx.getChild(1))
        if isinstance(notes, list):
            self.parti.extend([note[:1] + "'" + note[1:] for note in notes])
        else:
            self.parti.append(notes[:1] + "'" + notes[1:])
                
        
    def visitLooksheet(self, ctx):
        if not(len(self.parti)): print("Ninguna nota en la partitura")
        else:
            a = str(self.parti)
            a = a.replace(",","")
            a = a.replace('"','')
            print(a)
            
    def visitCondition(self,ctx):
        l = list(ctx.getChildren())
        if self.visit(l[1]) == 1:
            self.visit(l[3])
        elif len(l) > 5:
            if ctx.getChild(5).getText() == 'else':
                self.visit(ctx.inss(1))                
            
    def visitWhile_(self, ctx):
        while self.visit(ctx.getChild(1)) == 1:
            self.visit(ctx.getChild(3))
 
                   
    def visitString(self, ctx):
        return ctx.getChild(0).getText()[1:-1]

    
    def visitIns(self,ctx):
        return self.visitChildren(ctx)   
        
    def visitAssign(self, ctx):
        self.stack[-1][ctx.VAR().getText()] = self.visit(ctx.getChild(2))    
    
    
    def visitDiv(self, ctx):
        numerator = self.visit(ctx.getChild(0))
        denominator = self.visit(ctx.getChild(2))
        if denominator == 0:
            raise AlgoritmiaException('Division by zero.')
        return numerator / denominator

    def visitVar(self, ctx):
        return self.stack[-1][ctx.VAR().getText()]
    
        
    
    def visitMult(self, ctx):
        return self.visit(ctx.getChild(0)) * self.visit(ctx.getChild(2))    
    
    def visitLista(self, ctx):
        l = list(ctx.getChildren())
        values = [self.visit(child) for child in l[1:-1]]
        return values
    
    
    def visitSiz(self, ctx):
        return len(self.stack[-1][ctx.VAR().getText()])

    def visitNum(self, ctx):
        return int(ctx.NUM().getText())    

        
    def visitListrem(self, ctx):
        index = self.visit(ctx.expr())
        list_var = self.stack[-1][ctx.VAR().getText()]
        if 1 <= index <= len(list_var):
            del list_var[index - 1]
        else:
            raise AlgoritmiaException(f'Índice {index} no pertenece a la lista {ctx.VAR().getText()}')

    def visitParens(self, ctx):
        return self.visit(ctx.getChild(1))
    
    
    def visitProc(self,ctx):
        children = list(ctx.getChildren())
        name = children[0].getText()
        parametros = (self.visit(children[1]))

        
        if name in self.procs:
            self.__proc__(name,parametros)
        else:
            raise AlgoritmiaException('Proc \"' + name + '\" no definido.')
        
            
    def visitListadd(self, ctx):
        variable = ctx.VAR().getText()
        element = self.visit(ctx.getChild(2))
        self.stack[-1][variable].append(element)
    

    def getkey(self, val):
        for key, value in self.notes.items():
            if val == value:
                return key

    def visitPlus(self, ctx):
        left_child = self.visit(ctx.getChild(0))
        right_child = self.visit(ctx.getChild(2))
    
        if isinstance(left_child, str):
            left_child = self.notes[left_child]
        if isinstance(right_child, str):
            right_child = self.notes[right_child]
    
        result = left_child + right_child
        return self.getkey(result) if result in self.notes.values() else result 
     
   
    def visitProcDef (self,ctx):
        children = list(ctx.getChildren())
        name = children[0].getText()
        parametros = self.visit(children[1])
        if name in self.procs:
            raise AlgoritmiaException('Proc \"' + name + '\" ya definido.')
        
        else:
            self.procs[name] = Proceso(name,parametros,ctx.inss())
    
    
    def visitGt(self,ctx):
        l = list(ctx.getChildren())
        
        a = (self.stack[-1][ctx.expr(0).getText()] in self.notes.keys())
        b = (self.stack[-1][ctx.expr(1).getText()] in self.notes.keys())
        
        if a and b:
            self.adins = True
            nota1 = self.stack[-1][ctx.expr(0).getText()]
            val1 = self.notes[nota1]
            nota2 = self.stack[-1][ctx.expr(0).getText()]
            val2 = self.notes[nota2]
            return int(val1 > val2)
        if self.stack[-1][ctx.expr(0).getText()] in self.notes.keys():
            self.adins = True
            nota1 = self.stack[-1][ctx.expr(0).getText()]
            val1 = self.notes[nota1]
            nota2 = ctx.expr(1).getText()
            val2 = self.notes[nota2]
            return int(val1 > val2)
        if self.stack[-1][ctx.expr(1).getText()] in self.notes.keys():
            self.adins = True
            nota1 = ctx.expr(0).getText()
            val1 = self.notes[nota1]
            nota2 = self.stack[-1][ctx.expr(1).getText()]
            val2 = self.notes[nota2]
            return int(val1 > val2)
        else:
            if (not self.adins):
                return int(self.visit(l[0]) > self.visit(l[2]))
            else:
                return
            
        self.adins = False
    
    def visitLt(self, ctx):
        left_child = self.stack[-1].get(ctx.getChild(0).getText(), self.visit(ctx.getChild(0)))
        right_child = self.stack[-1].get(ctx.getChild(1).getText(), self.visit(ctx.getChild(1)))
    
        if isinstance(left_child, str):
            left_child = self.notes[left_child]
        if isinstance(right_child, str):
            right_child = self.notes[right_child]
    
        return int(left_child < right_child)    
    
    
    def visitConsult(self, ctx):
        index = self.visit(ctx.expr())
        list_var = self.stack[-1][ctx.VAR().getText()]
        if 1 <= index <= len(list_var):
            return list_var[index - 1]
        else:
            raise AlgoritmiaException(f'Índice {index} no pertenece a la lista {ctx.VAR().getText()}')

    def visitNota(self, ctx):
        note = ctx.NOTA().getText()
        return note if len(note) > 1 else note + "4"    
    
    
    def visitLte(self, ctx):
        left_text = ctx.expr(0).getText()
        right_text = ctx.expr(1).getText()
        left_value = self.notes.get(left_text, self.visit(ctx.expr(0)))
        right_value = self.notes.get(right_text, self.visit(ctx.expr(1)))
        return int(left_value <= right_value)    

           
    
    def visitMin(self,ctx):
        l = list(ctx.getChildren())
        if (ctx.getChild(0).getText() in self.notes.keys()):
            nota = ctx.expr(0).getText()
            val1 = self.notes[nota]
            result = val1 - self.visit(l[2])
            for key,value in self.notes.items():
                if result == value:
                    nova_nota = key
                    return nova_nota
        elif (ctx.getChild(2).getText() in self.notes.keys()):
            nota = ctx.expr(1).getText()
            val1 = self.notes[nota]
            result = val1 - self.visit(l[0])
            for key,value in self.notes.items():
                if result == value:
                    nova_nota = key
                    return nova_nota
        elif (self.stack[-1][ctx.expr(0).getText()] in self.notes.keys()):
            nota = self.stack[-1][ctx.expr(0).getText()]
            val1 = self.notes[nota]
            result = val1 - self.visit(l[2])
            for key,value in self.notes.items():
                if result == value:
                    nova_nota = key
                    return nova_nota
        elif (self.stack[-1][ctx.expr(1).getText()] in self.notes.keys()):
            nota = self.stack[-1][ctx.expr(1).getText()]
            val1 = self.notes[nota]
            result = val1 - self.visit(l[0])
            for key,value in self.notes.items():
                if result == value:
                    nova_nota = key
                    return nova_nota

        else:
            return self.visit(l[0]) - self.visit(l[2]) 
        
    
    def visitNeq(self,ctx):
        l = list(ctx.getChildren())
        
        a = (self.stack[-1][ctx.expr(0).getText()] in self.notes.keys())
        b = (self.stack[-1][ctx.expr(1).getText()] in self.notes.keys())
        
        if a and b:
            self.adins = True
            nota1 = self.stack[-1][ctx.expr(0).getText()]
            val1 = self.notes[nota1]
            nota2 = self.stack[-1][ctx.expr(0).getText()]
            val2 = self.notes[nota2]
            return int(val1 != val2)
        if (a):
            self.adins = True
            nota1 = self.stack[-1][ctx.expr(0).getText()]
            val1 = self.notes[nota1]
            nota2 = ctx.expr(1).getText()
            val2 = self.notes[nota2]
            return int(val1 != val2)
        if (b):
            self.adins = True
            nota1 = ctx.expr(0).getText()
            val1 = self.notes[nota1]
            nota2 = self.stack[-1][ctx.expr(1).getText()]
            val2 = self.notes[nota2]
            return int(val1 != val2)
        # enter == enter
        else:
            if (not self.adins):
                return int(self.visit(l[0]) != self.visit(l[2]))
            else:
                return
            
        self.adins = False
    

