from random import random
import OpenGL.GL as GL
import pyrr
import numpy as np 
import glutils
from random import randint


class Transformation3D: 
    def __init__(self, euler = pyrr.euler.create(), center = pyrr.Vector3(), translation = pyrr.Vector3()):
        self.rotation_euler = euler.copy()
        self.rotation_center = center.copy()
        self.translation = translation.copy()

class Object:
    def __init__(self, vao, nb_triangle, program, texture):
        self.vao = vao
        self.nb_triangle = nb_triangle
        self.program = program
        self.texture = texture
        self.visible = True

    def draw(self):
        if self.visible : 
            GL.glUseProgram(self.program)
            GL.glBindVertexArray(self.vao)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glDrawElements(GL.GL_TRIANGLES, 3*self.nb_triangle, GL.GL_UNSIGNED_INT, None)

class Object3D(Object):
    def __init__(self, vao, nb_triangle, program, texture, transformation):
        super().__init__(vao, nb_triangle, program, texture)
        self.transformation = transformation

    def draw(self):
        GL.glUseProgram(self.program)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "translation_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_model")
        # Modifie la variable pour le programme courant
        translation = self.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "rotation_center_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_model")
        # Modifie la variable pour le programme courant
        rotation_center = self.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(self.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(self.program, "rotation_model")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_model")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)

        super().draw()


class Camera:
    def __init__(self, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 100)):
        self.transformation = transformation
        self.projection = projection

class Text(Object):


    
    def __init__(self, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
        self.value = value
        self.bottomLeft = bottomLeft
        self.topRight = topRight
        super().__init__(vao, nb_triangle, program, texture)

    def draw(self):
        GL.glUseProgram(self.program)
        GL.glDisable(GL.GL_DEPTH_TEST)
        size = self.topRight-self.bottomLeft
        size[0] /= len(self.value)
        size[1] /= 4
        loc = GL.glGetUniformLocation(self.program, "size")
        if (loc == -1) :
            print("Pas de variable uniforme : size")
        GL.glUniform2f(loc, size[0], size[1])
        GL.glBindVertexArray(self.vao)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        for idx, c in enumerate(self.value):
            loc = GL.glGetUniformLocation(self.program, "start")
            if (loc == -1) :
                print("Pas de variable uniforme : start")
            GL.glUniform2f(loc, self.bottomLeft[0]+idx*size[0], self.bottomLeft[1])

            loc = GL.glGetUniformLocation(self.program, "c")
            if (loc == -1) :
                print("Pas de variable uniforme : c")
            GL.glUniform1i(loc, np.array(ord(c), np.int32))

            GL.glDrawElements(GL.GL_TRIANGLES, 3*2, GL.GL_UNSIGNED_INT, None)
        GL.glEnable(GL.GL_DEPTH_TEST)

    @staticmethod
    def initalize_geometry():
        p0, p1, p2, p3 = [0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]
        geometrie = np.array([p0+p1+p2+p3], np.float32)
        index = np.array([[0, 1, 2]+[0, 2, 3]], np.uint32)
        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, geometrie, GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        vboi = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,vboi)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,index,GL.GL_STATIC_DRAW)
        return vao

class Arme():
    def __init__(self,vao,program3d_id,nb_tr,viewer):
        self.vao=vao
        self.texture=glutils.load_texture('stegosaurus.jpg')
        self.program=program3d_id
        self.nb_tr=nb_tr
        self.viewer=viewer
        self.nb_objets=len(viewer.objs)
        self.projectiles=[]# Liste des projectiles
        self.fire_rate=20 #cadence de tir
        self.proj_intervalles=self.fire_rate

    def tir(self):
        if self.proj_intervalles==self.fire_rate:
            self.tr=Transformation3D()
            o = Object3D(self.vao, self.nb_tr, self.program, self.texture, self.tr) 
            self.viewer.add_object(o) 
            self.projectiles.append(Projectile(o,self.viewer))
            self.projectiles[-1].trajectoire()
            self.proj_intervalles=0
        
    def mouvement_projectile(self):
        for ind,proj in enumerate(self.projectiles):
            if proj.detruit==False:
                proj.mouvement()
            else:
                self.projectiles.pop(ind)
                for ind,obj in enumerate(self.viewer.objs):
                    if obj==proj.objet:
                        self.viewer.remove_object(ind)
                            
        if self.proj_intervalles<self.fire_rate:
            self.proj_intervalles+=1

class Projectile():
    def __init__(self,o,viewer):
        self.objet=o
        self.viewer=viewer
        self.tir=False
        self.temps_vol=0
        self.detruit=False
        self.angle=0
    def trajectoire(self):
        self.objet.transformation.translation = self.viewer.objs[0].transformation.translation.copy() + pyrr.Vector3([0, 0.13, 0])
        self.angle=pyrr.matrix33.create_from_eulers(self.viewer.objs[0].transformation.rotation_euler.copy())
        self.tir=True

    def mouvement(self): 
        if self.tir==True:
            self.objet.transformation.translation+= \
                pyrr.matrix33.apply_to_vector(self.angle, pyrr.Vector3([0, 0, 2]))
            self.temps_vol+=1
            if self.temps_vol==30:
                self.destruction_projectile()

    def destruction_projectile(self):
        self.tir=False
        self.objet.visible=False
        self.detruit=True

class Wave():
    def __init__(self,vao,program3d_id,nb_tr,viewer):
        self.vao=vao
        self.texture=glutils.load_texture('stegosaurus.jpg')
        self.program=program3d_id
        self.nb_tr=nb_tr
        self.viewer=viewer
        self.nb_objets=len(viewer.objs)
        self.enemies=[]
        self.wave_size=5


    def enemy_init(self):
        if len(self.enemies)<self.wave_size:
            for nb in range(self.wave_size):
                self.tr=Transformation3D()
                o = Object3D(self.vao, self.nb_tr, self.program, self.texture, self.tr)
                self.viewer.add_object(o) 
                self.enemies.append(Enemy(o,self.viewer,nb))
                self.enemies[-1].spawn()

    def wave_movement(self):
        for ind,enem in enumerate(self.enemies):
            if enem.detruit==False:
                enem.direction()

    def check_hit(self,projectiles):
        for ind,enem in enumerate(self.enemies):
            enem.enemy_hit(projectiles)
            enem.joueur_hit()
            if enem.detruit==True:
                self.enemies.pop(ind)
                for ind,obj in enumerate(self.viewer.objs):
                    if obj==enem.objet:
                        self.viewer.remove_object(ind)
class Enemy():
    def __init__(self,o,viewer,position):
        self.objet=o
        self.viewer=viewer
        self.detruit=False
        self.position=position
    def spawn(self):
        
        self.angle=pyrr.matrix33.create_from_eulers(self.viewer.objs[0].transformation.rotation_euler.copy())
        self.objet.transformation.translation = self.viewer.objs[0].transformation.translation.copy() + pyrr.matrix33.apply_to_vector(self.angle, pyrr.Vector3([self.position*2, 0, 20]))
  
    def direction(self): 
        self.angle=pyrr.matrix33.create_from_eulers(self.viewer.objs[0].transformation.rotation_euler.copy())
        self.objet.transformation.translation-= \
            pyrr.matrix33.apply_to_vector(self.angle, pyrr.Vector3([0, 0, 0.05*randint(1,3)]))

    def destruction_enemy(self,proj):
        self.tir=False
        self.detruit=True
        self.objet.visible=False
        proj.destruction_projectile()
   
    def enemy_hit(self,projectiles):
        coordO=self.objet.transformation.translation
        for ind,proj in enumerate(projectiles):
            coordP=proj.objet.transformation.translation
            norme=\
                np.sqrt((coordO.x-coordP.x)**2  + (coordO.y-coordP.y)**2  + (coordO.z-coordP.z)**2 )
            if norme<=1.5:
                self.destruction_enemy(proj)
    
    def joueur_hit(self):
        coordO=self.objet.transformation.translation
        coordP=self.viewer.objs[0].transformation.translation
        norme=\
                np.sqrt((coordO.x-coordP.x)**2  + (coordO.y-coordP.y)**2  + (coordO.z-coordP.z)**2 )
        if norme<=1.5:
            self.viewer.objs[2].value='Mort'
            self.viewer.game_over=True
    
    
        
    