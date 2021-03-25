import tkinter as tk
import string #for a string to store alphabet
import os, sys #help with importing images
from PIL import Image, ImageTk #help with implementing images into GUI
from PIL.ImageTk import PhotoImage

class Board(tk.Frame):

    def __init__(self, parent, length, width): #self=Frame, parent=root
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.length = length
        self.width = width
        self.config(height=100*self.length, width=100*self.width)
        self.pack()
        
        self.square_color = None
        self.squares = {} #stores squares with pos as key and button as value
        self.ranks = string.ascii_lowercase
        self.white_images = {} #stores images of pieces
        self.black_images = {}
        self.white_pieces = ["pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7"] #for convenience when calling all white pieces
        self.black_pieces = ["pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"]
        self.buttons_pressed = 0
        self.turns = 0
        self.sq1 = None #first square clicked
        self.sq2 = None 
        self.sq1_button = None #button associated with the square clicked
        self.sq2_button = None
        self.piece_color = None
        self.wk_moved = False #for castling
        self.bk_moved = False
        self.wr1_moved = False
        self.wr2_moved = False
        self.br1_moved = False
        self.br2_moved = False
        self.castled = False
        self.set_squares()

    def select_piece(self, button): #called when a square button is pressed, consists of majority of the movement code
        if button["image"] in self.white_pieces and self.buttons_pressed == 0: #checks color of first piece
            self.piece_color = "white"
        elif button["image"] in self.black_pieces and self.buttons_pressed == 0:
            self.piece_color = "black"      
        
        if (self.piece_color == "white" and self.turns % 2 == 0) or (self.piece_color == "black" and self.turns % 2 == 1) or self.buttons_pressed == 1: #prevents people from moving their pieces when it's not their turn
            if self.buttons_pressed == 0: #stores square and button of first square selected
                self.sq1 = list(self.squares.keys())[list(self.squares.values()).index(button)] #retrieves pos of piece
                self.sq1_button = button
                self.buttons_pressed += 1
             
            elif self.buttons_pressed==1: #stores square and button of second square selected
                self.sq2 = list(self.squares.keys())[list(self.squares.values()).index(button)]
                self.sq2_button = button
                if self.sq2 == self.sq1: #prevents self-destruction and allows the user to choose a new piece
                    self.buttons_pressed = 0
                    return
                
                if self.allowed_piece_move() and self.friendly_fire() == False: #makes sure the move is legal
                    prev_sq1 = self.sq1
                    prev_sq1_button_piece = self.sq1_button["image"]
                    prev_sq2 = self.sq2
                    prev_sq2_button_piece = self.sq2_button["image"]
                    self.squares[self.sq2].config(image=self.sq1_button["image"]) #moves pice in sq1 to sq2
                    self.squares[self.sq2].image = self.sq1_button["image"]
                    self.squares[self.sq1].config(image=self.white_images["blank.png"]) #clears sq1
                    self.squares[self.sq1].image = self.white_images["blank.png"]
                    if  self.in_check() == True and self.castled == False: #for some reason it says king is in check after a castle so I set up a variable here that would prevent this code from running
                        self.squares[prev_sq2].config(image=prev_sq2_button_piece) #reverts movement since king is or would be put into check because of move
                        self.squares[prev_sq2].image = prev_sq2_button_piece
                        self.squares[prev_sq1].config(image=prev_sq1_button_piece)
                        self.squares[prev_sq1].image = prev_sq1_button_piece
                        self.buttons_pressed = 0
                        return
                    else: #runs if king is not in check, checks if kings or rooks have moved, preventing castling in the future
                        if prev_sq1_button_piece == "pyimage3":
                            self.wk_moved = True
                        if prev_sq1_button_piece == "pyimage10":
                            self.bk_moved = True
                        if prev_sq1_button_piece == "pyimage7" and prev_sq1 == "a1":
                            self.wr1_moved = True
                        if prev_sq1_button_piece == "pyimage7" and prev_sq1 == "h1":
                            self.wr2_moved = True
                        if prev_sq1_button_piece == "pyimage14" and prev_sq1 == "a8":
                            self.br1_moved = True
                        if prev_sq1_button_piece == "pyimage14" and prev_sq1 == "h8":
                            self.br2_moved = True
                        self.buttons_pressed = 0
                        self.turns += 1                     
                        if (button["image"] == "pyimage5" and prev_sq2.count("8")==1) or (button["image"] == "pyimage12" and prev_sq2.count("1")==1): #checks for possible pawn promotion
                            self.promotion_menu(self.piece_color)
                        self.castled = False
        else:
            self.buttons_pressed = 0
            return

    def promotion_menu(self, color): #creates menu to choose what piece to change the pawn to
        def return_piece(piece): #function called by buttons to make the change and destroy window
            self.squares[self.sq2].config(image=piece)
            self.squares[self.sq2].image = piece
            promo.destroy()
            return
        
        promo = tk.Tk() #creates a new menu with buttons depending on pawn color
        promo.title("Choose what to promote your pawn to")
        if color=="white":
            promo_knight = tk.Button(promo, text="Knight", command=lambda: return_piece("pyimage4")) #triggers return_piece function when selected
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(promo, text="Bishop", command=lambda: return_piece("pyimage1"))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(promo, text="Rook", command=lambda: return_piece("pyimage7"))
            promo_rook.grid(row=1, column=0)
            promo_queen = tk.Button(promo, text="Queen", command=lambda: return_piece("pyimage6"))
            promo_queen.grid(row=1, column=1)
        elif color=="black":
            promo_knight = tk.Button(promo, text="Knight", command=lambda: return_piece("pyimage11"))
            promo_knight.grid(row=0, column=0)
            promo_bishop = tk.Button(promo, text="Bishop", command=lambda: return_piece("pyimage8"))
            promo_bishop.grid(row=0, column=1)
            promo_rook = tk.Button(promo, text="Rook", command=lambda: return_piece("pyimage14"))
            promo_rook.grid(row=1, column=0)
            promo_queen = tk.Button(promo, text="Queen", command=lambda: return_piece("pyimage13"))
            promo_queen.grid(row=1, column=1)
        promo.mainloop()
        return
            
    def friendly_fire(self): #prevents capturing your own pieces
        piece_2_color = self.sq2_button["image"]
        if self.piece_color == "white" and piece_2_color in self.white_pieces:
            return True
        if self.piece_color == "black" and piece_2_color in self.black_pieces:
            return True
        else:
            return False
        
    def clear_path(self, piece): #makes sure that the squares in between sq1 and sq2 aren't occupied
        if piece == "rook" or piece == "queen":   
            if self.sq1[0] == self.sq2[0]: #for vertical movement
                pos1 = min(int(self.sq1[1]), int(self.sq2[1]))
                pos2 = max(int(self.sq1[1]), int(self.sq2[1]))
                for i in range(pos1+1, pos2):
                    square_on_path = self.squares[self.sq1[0]+str(i)].cget("image")
                    if square_on_path != "pyimage2":
                        return False
                    
            elif self.sq1[1] == self.sq2[1]: #for horizontal movement
                pos1 = min(self.ranks.find(self.sq1[0]), self.ranks.find(self.sq2[0]))
                pos2 = max(self.ranks.find(self.sq1[0]), self.ranks.find(self.sq2[0]))

                for i in range(pos1+1, pos2):
                    square_on_path = self.squares[self.ranks[i]+self.sq1[1]].cget("image")
                    if square_on_path != "pyimage2":
                        return False
                    
        if piece == "bishop" or piece == "queen": #for diagonal movement
            x1 = self.ranks.find(self.sq1[0])
            x2 = self.ranks.find(self.sq2[0])
            y1 = int(self.sq1[1])
            y2 = int(self.sq2[1])
            
            if  y1<y2:
                if x1<x2: #NE direction
                    for x in range(x1+1, x2):
                        y1 += 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
                elif x1>x2: #NW direction
                    for x in range(x1-1, x2, -1):
                        y1 += 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
            elif y1>y2:
                if x1<x2: #SE direction
                    for x in range(x1+1, x2):
                        y1 -= 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
                if x1>x2: #SW direction
                    for x in range(x1-1, x2, -1):
                        y1 -= 1
                        square_on_path = self.squares[self.ranks[x]+str(y1)].cget("image")
                        if square_on_path != "pyimage2":
                            return False
        return True
                
        
    def allowed_piece_move(self): #checks whether the piece can move to square 2 with respect to their movement capabilities
        wb, wk, wn, wp, wq, wr = "pyimage1", "pyimage3", "pyimage4", "pyimage5", "pyimage6", "pyimage7" #redefining pyimages for readability
        bb, bk, bn, bp, bq, br = "pyimage8", "pyimage10", "pyimage11", "pyimage12", "pyimage13", "pyimage14"

        if self.sq1_button["image"] == "pyimage2" or self.sq1_button["image"] == "pyimage9": #for when this function is called for check
            return False
        
        if (self.sq1_button["image"] == wb or self.sq1_button["image"] == bb) and self.clear_path("bishop"): #bishop movement        
            if abs(int(self.sq1[1]) - int(self.sq2[1])) == abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])): #makes sure there is equal change between file and rank movement
                return True

        if self.sq1_button["image"] == wn or self.sq1_button["image"] == bn: #knight movement
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) == 2) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 1): #allows tall L moves
                return True
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) == 1) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 2): #allows wide L moves
                return True
        
        if self.sq1_button["image"] == wk or self.sq1_button["image"] == bk: #king movement
            if (abs(int(self.sq1[1]) - int(self.sq2[1])) < 2) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0]))) < 2: #allows 1 square moves
                return True
            if self.castle() is True:
                return True
        
        if self.sq1_button["image"] == wp: #white pawn movement
            if "2" in self.sq1: #allows for 2 space jump from starting pos
                if (int(self.sq1[1])+1 == int(self.sq2[1]) or int(self.sq1[1])+2 == int(self.sq2[1])) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2": #allows 2 sq movement
                    in_front = self.squares[self.sq1[0] + str(int(self.sq1[1])+1)]
                    if in_front["image"] == "pyimage2": #makes sure that there is no piece blocking path
                        return True
            if int(self.sq1[1])+1 == int(self.sq2[1]) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2": #allows 1 sq movement
                    return True
            if int(self.sq1[1])+1 == int(self.sq2[1]) and (abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0]))) == 1 and self.sq2_button["image"] != "pyimage2": #allows the capturing of diagonal pieces
                    return True

                
        if self.sq1_button["image"] == bp: #black pawn movement
            if "7" in self.sq1: #allows for 2 space jump from starting pos
                if (int(self.sq1[1]) == int(self.sq2[1])+1 or int(self.sq1[1]) == int(self.sq2[1])+2) and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2": #only allows it to move straight 1 or 2 sq
                    return True
            if int(self.sq1[1]) == int(self.sq2[1])+1 and self.sq1[0] == self.sq2[0] and self.sq2_button["image"] == "pyimage2":
                    return True
            if int(self.sq1[1]) == int(self.sq2[1])+1 and abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])) == 1 and self.sq2_button["image"] != "pyimage2": #allows the capturing of diagonal pieces if there is an opponent piece there
                    return True

        if (self.sq1_button["image"] == wq or self.sq1_button["image"] == bq) and self.clear_path("queen"): #queen movement
            if int(self.sq1[1]) == int(self.sq2[1]) or self.sq1[0] == self.sq2[0]: #only allows movement within same rank or file
                return True
            if abs(int(self.sq1[1]) - int(self.sq2[1])) == abs(self.ranks.find(self.sq1[0]) - self.ranks.find(self.sq2[0])):
                return True
        
        if self.sq1_button["image"] == wr or self.sq1_button["image"] == br: #rook movement
            if (int(self.sq1[1]) == int(self.sq2[1]) or self.sq1[0] == self.sq2[0]) and self.clear_path("rook"): #only allows movement within same rank or file
                return True  
        return False
    
    def castle(self): #checks to see if the move entails a castle, and if a castle is allowed
        if self.wk_moved == False: #makes sure king hasn't moved
            if self.wr1_moved == False and self.sq2 == "c1": #finds out which way user wants to castle and if the rook has moved (in this case white would want to castle to the left)
                for x in range(1,4): #checks to see if squares in between rook and king are empty and are not a possible move for opponent
                    square_button = self.squares[self.ranks[x]+str(1)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["a1"].config(image="pyimage2")
                    self.squares["a1"].image = "pyimage2"
                    self.squares["d1"].config(image="pyimage7")
                    self.squares["d1"].image = ("pyimage7")
                    self.castled = True
                    return True
            if self.wr2_moved == False and self.sq2 == "g1":
                for x in range(5,7): #checks to see if squares in between rook and king are empty and are not a possible move for opponent
                    square_button = self.squares[self.ranks[x]+str(1)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["h1"].config(image="pyimage2")
                    self.squares["h1"].image = "pyimage2"
                    self.squares["f1"].config(image="pyimage7")
                    self.squares["f1"].image = ("pyimage7")
                    self.castled = True
                    return True
        if self.bk_moved == False:
            if self.br1_moved == False and self.sq2 == "c8":
                for x in range(1,3): #checks to see if squares in between rook and king are empty and are not a possible move for opponent
                    square_button = self.squares[self.ranks[x]+str(8)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["a8"].config(image="pyimage2")
                    self.squares["a8"].image = "pyimage2"
                    self.squares["d8"].config(image="pyimage14")
                    self.squares["d8"].image = ("pyimage14")
                    self.castled = True
                    return True
            if self.br2_moved == False and self.sq2 == "g8":
                for x in range(5,7): #checks to see if squares in between rook and king are empty and are not a possible move for opponent
                    square_button = self.squares[self.ranks[x]+str(8)]
                    if square_button["image"] != "pyimage2":
                        return False
                    self.squares["h8"].config(image="pyimage2")
                    self.squares["h8"].image = "pyimage2"
                    self.squares["f8"].config(image="pyimage14")
                    self.squares["f8"].image = ("pyimage14")
                    self.castled = True
                    return True
        else:
            return False
   
        self.bk_moved = False
        self.wr1_moved = False
        self.wr2_moved = False
        self.br1_moved = False
        self.br2_moved = False

    def in_check(self): #prevents a move if king is under attack
        previous_sq1 = self.sq1 #stores current values assigned to values
        previous_sq1_button = self.sq1_button
        previous_sq2 = self.sq2
        previous_sq2_button = self.sq2_button
        
        def return_previous_values():
            self.sq1 = previous_sq1
            self.sq1_button = previous_sq1_button
            self.sq2 = previous_sq2
            self.sq2_button = previous_sq2_button
            
        if self.piece_color == "white":
            self.sq2 = self.find_king("pyimage3") #calls find_king function to find pos of king
            for key in self.squares: #iterates through each square
                self.sq1 = key
                self.sq1_button = self.squares[self.sq1]
                if self.sq1_button["image"] in self.black_pieces:
                    if self.allowed_piece_move(): #checks to see if the king's current pos is a possible move for the piece
                        return True
        if self.piece_color == "black":
            self.sq2 = self.find_king("pyimage10")
            for key in self.squares:
                self.sq1 = key
                self.sq1_button = self.squares[self.sq1] 
                if self.sq1_button["image"] in self.white_pieces:
                    if self.allowed_piece_move():
                        return True
        return_previous_values()
        return False
    
    def find_king(self, king): #finds the square where the king is currently on
        for square  in self.squares:
            button = self.squares[square]
            if button["image"] == king:
                return square
    
    def set_squares(self): #fills frame with buttons representing squares

        for x in range(8):
            for y in range(8):
                if x%2==0 and y%2==0: #alternates between dark/light tiles
                    self.square_color="tan4" 
                elif x%2==1 and y%2==1:
                    self.square_color="tan4"
                else:
                    self.square_color="burlywood1"
                    
                B = tk.Button(self, bg=self.square_color, activebackground="lawn green")
                B.grid(row=8-x, column=y)
                pos = self.ranks[y]+str(x+1)
                self.squares.setdefault(pos, B) #creates list of square positions
                self.squares[pos].config(command= lambda key=self.squares[pos]: self.select_piece(key))               
        
    def import_pieces(self): #opens and stores images of pieces and prepares the pieces for the game for both sides
        path = os.path.join(os.path.dirname(__file__), "White") #stores white pieces images into dicts
        w_dirs = os.listdir(path)
        for file in w_dirs:
            img = Image.open(path+"\\"+file)
            img = img.resize((80,80), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image=img)
            self.white_images.setdefault(file, img)

        path = os.path.join(os.path.dirname(__file__), "Black") #stores black pieces images into dicts
        b_dirs = os.listdir(path)
        for file in b_dirs:
            img = Image.open(path+"\\"+file)
            img = img.resize((80,80), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image=img)
            self.black_images.setdefault(file, img)

    def set_pieces(self): #places pieces in starting positions
        dict_rank1_pieces = {"a1":"r.png", "b1":"n.png", "c1":"b.png", "d1":"q.png", "e1":"k.png", "f1":"b.png", "g1":"n.png", "h1":"r.png"} #assigning positions with their default pieces
        dict_rank2_pieces = {"a2":"p.png", "b2":"p.png", "c2":"p.png", "d2":"p.png", "e2":"p.png", "f2":"p.png", "g2":"p.png", "h2":"p.png"}     
        dict_rank7_pieces = {"a7":"p.png", "b7":"p.png", "c7":"p.png", "d7":"p.png", "e7":"p.png", "f7":"p.png", "g7":"p.png", "h7":"p.png"}
        dict_rank8_pieces = {"a8":"r.png", "b8":"n.png", "c8":"b.png", "d8":"q.png", "e8":"k.png", "f8":"b.png", "g8":"n.png", "h8":"r.png"}

        for key in dict_rank1_pieces: #inserts images into buttons
            starting_piece = dict_rank1_pieces[key]
            self.squares[key].config(image=self.white_images[starting_piece])
            self.squares[key].image = self.white_images[starting_piece]
            
        for key in dict_rank2_pieces:
            starting_piece = dict_rank2_pieces[key]
            self.squares[key].config(image=self.white_images[starting_piece])
            self.squares[key].image = self.white_images[starting_piece]
            
        for key in dict_rank7_pieces:
            starting_piece = dict_rank7_pieces[key]
            self.squares[key].config(image=self.black_images[starting_piece])
            self.squares[key].image = self.black_images[starting_piece]
            
        for key in dict_rank8_pieces:
            starting_piece = dict_rank8_pieces[key]
            self.squares[key].config(image=self.black_images[starting_piece])
            self.squares[key].image = self.black_images[starting_piece]

        for rank in range(3,7): #fill rest with blank pieces
            for file in range(8):
                starting_piece = "blank.png"
                pos = self.ranks[file]+str(rank)
                self.squares[pos].config(image=self.white_images[starting_piece])
                self.squares[pos].image = self.white_images[starting_piece]

root = tk.Tk() #creates main window with the board and creates board object
root.geometry("800x800")
board = Board(root, 8, 8)
board.import_pieces()
board.set_pieces()
board.mainloop()
