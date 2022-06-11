from viewerGL import ViewerGL
import glutils
from mesh import Mesh
from cpe3d import Object3D, Camera, Transformation3D, Text, Arme
import numpy as np
import OpenGL.GL as GL
import pyrr


def main():
    viewer = ViewerGL()

    viewer.set_camera(Camera())
    viewer.cam.transformation.translation.y = 2
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    program3d_id = glutils.create_program_from_file('shader.vert', 'shader.frag') # scène 3d
    programGUI_id = glutils.create_program_from_file('gui.vert', 'gui.frag') # affichage texte sur l'écran

    m = Mesh.load_obj('stegosaurus.obj') #importation de la maille du stegosaure
    m.normalize() #coordonnées du stégo en -1 et 1 pour x, y et z transformation proportionnelle, objet centré donc
    m.apply_matrix(pyrr.matrix44.create_from_scale([1.5, 1.5, 1.5, 1])) # changement d'echelle de l'objet
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1] #les pieds de l'objet à 0, le 1 represente le y
    tr.translation.z = -5
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('stegosaurus.jpg') #lecture de l'image chargement sur le cpe et renvoie de l'id de limage sur le gpu
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr) # teq au travail fait par au vao et vbo, les infos du stegosaure sont sur le gpu avec load to gpu, le cpu en a plus besoin
    viewer.add_object(o) # ajout des objets sur le viewer

    #creation bloc herbe
    m = Mesh() #creation d'un nouveau maillage
    p0, p1, p2, p3 = [-25, 0, -25], [25, 0, -25], [25, 0, 25], [-25, 0, 25] # coord de text, morceau de plan y=0
    n, c = [0, 1, 0], [1, 1, 1]
    t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
    m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
    m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
    texture = glutils.load_texture('grass.jpg')
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D()) #objet 3d
    viewer.add_object(o)

    

    #chargement du texte
    vao = Text.initalize_geometry()
    texture = glutils.load_texture('fontB.jpg') 
    o = Text(' ', np.array([-0.8, 0.3], np.float32), np.array([0.8, 0.8], np.float32), vao, 2, programGUI_id, texture)
    viewer.add_object(o)
    o = Text('       .       ', np.array([-0.5, -0.2], np.float32), np.array([0.5, 0.3], np.float32), vao, 2, programGUI_id, texture) # objet texte
    viewer.add_object(o)


    m = Mesh().load_obj('cube.obj') #creation d'un nouveau maillage
    m.normalize() #coordonnées du stégo en -1 et 1 pour x, y et z transformation proportionnelle, objet centré donc
    m.apply_matrix(pyrr.matrix44.create_from_scale([0.01, 0.01, 0.03, 1])) # changement d'echelle de l'objet
    vao=m.load_to_gpu()
    nb_tr=m.get_nb_triangles()
    tr = Transformation3D()
    tr.translation.y = -np.amin(m.vertices, axis=0)[1] #les pieds de l'objet à 0, le 1 represente le y
    tr.translation.z = -5
    tr.rotation_center.z = 0.2
    texture = glutils.load_texture('stegosaurus.jpg') #lecture de l'image chargement sur le cpe et renvoie de l'id de limage sur le gpu
    #o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr) # teq au travail fait par au vao et vbo, les infos du stegosaure sont sur le gpu avec load to gpu, le cpu en a plus besoin
    #viewer.add_object(o) # ajout des objets sur le viewer

    weapon=Arme(vao,program3d_id,nb_tr,viewer)
    viewer.add_weapon(weapon)



    viewer.run()


if __name__ == '__main__':
    main()