import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image

import numpy as np


viewer = [0.0, 0.0, 10.0]

theta = 0.0
pix2angle = 1.0

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

image = Image.open("tekstura.tga")
image2 = Image.open("shrek.tga")
active_texture = 0 # 0 - domyslna tekstura, 1 - druga tekstura (shrek)

N = 30


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(
        GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0,
        GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1)
    )


def shutdown():
    pass


def generateEgg(n):
    tab = np.zeros((n+1, n+1, 3))

    # Równomierne rozłożenie wartości dla parametrów u i v
    u_values = np.linspace(0.0, 1.0, n+1)
    v_values = np.linspace(0.0, 1.0, n+1)

    # Wypełnianie tablicy współrzędnymi x, y, z dla każdej pary (u, v)
    for i, u in enumerate(u_values):
        for j, v in enumerate(v_values):
            x = (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * np.cos(np.pi * v)
            y = 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2 - 5
            z = (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * np.sin(np.pi * v)
            tab[i, j] = [x, y, z]

    return tab


def generateEggVectors(n):
    tab = np.zeros((n+1, n+1, 3))

    for i in range(0, n+1):
        for j in range(0, n+1):
            u = i / n
            v = j / n

            xu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * np.cos(np.pi * v)
            xv = np.pi * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * np.sin(np.pi * v)
            yu = 640 * pow(u, 3) - 960 * pow(u, 2) + 320 * u
            yv = 0
            zu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * np.sin(np.pi * v)
            zv = (- np.pi) * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * np.cos(np.pi * v)

            x = yu * zv - zu * yv
            y = zu * xv - xu * zv
            z = xu * yv - yu * xv

            sum = pow(x, 2) + pow(y, 2) + pow(z, 2)
            length = np.sqrt(sum)

            if length > 0:
                x = x / length
                y = y / length
                z = z / length

            if i > n / 2:
                x *= -1
                y *= -1
                z *= -1

            tab[i][j][0] = x
            tab[i][j][1] = y
            tab[i][j][2] = z

    return tab


def generateEggTextures(n):
    tab = np.zeros((n+1, n+1, 2))

    for i in range(0, n+1):
        for j in range(0, n+1):
            u = i / n
            v = j / n

            # obrocenie tekstury na wlasciwej polowce
            if (i > (n / 2)):
                tab[i][j][0] = v
                tab[i][j][1] = 1 - 2 * u
            else:
                tab[i][j][0] = v
                tab[i][j][1] = 2 * u

    return tab


def render(time):
    global theta

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle

    glRotatef(theta, 0.0, 1.0, 0.0)

    tab = generateEgg(N)
    tab_vectors = generateEggVectors(N)
    tab_texture = generateEggTextures(N)

    for i in range(N):
        for j in range(N):

            if (i > (N / 2)):
                glFrontFace(GL_CW)
            else:
                glFrontFace(GL_CCW)

            glBegin(GL_TRIANGLES)

            # Trójkąt między punktami (i, j), (i+1, j), (i, j+1)
            glTexCoord2f(tab_texture[i, j, 0], tab_texture[i, j, 1])
            glNormal3f(tab_vectors[i, j, 0], tab_vectors[i, j, 1], tab_vectors[i, j, 2])
            glVertex3f(tab[i, j, 0], tab[i, j, 1], tab[i, j, 2])

            glTexCoord2f(tab_texture[i+1, j, 0], tab_texture[i+1, j, 1])
            glNormal3f(tab_vectors[i+1, j, 0], tab_vectors[i+1, j, 1], tab_vectors[i+1, j, 2])
            glVertex3f(tab[i + 1, j, 0], tab[i + 1, j, 1], tab[i + 1, j, 2])

            glTexCoord2f(tab_texture[i, j+1, 0], tab_texture[i, j+1, 1])
            glNormal3f(tab_vectors[i, j+1, 0], tab_vectors[i, j+1, 1], tab_vectors[i, j+1, 2])
            glVertex3f(tab[i, j + 1, 0], tab[i, j + 1, 1], tab[i, j + 1, 2])

            # Trójkąt dopełniający - między punktami (i+1, j), (i+1, j+1), (i, j+1)
            glTexCoord2f(tab_texture[i+1, j, 0], tab_texture[i+1, j, 1])
            glNormal3f(tab_vectors[i+1, j, 0], tab_vectors[i+1, j, 1], tab_vectors[i+1, j, 2])
            glVertex3f(tab[i + 1, j, 0], tab[i + 1, j, 1], tab[i + 1, j, 2])

            glTexCoord2f(tab_texture[i + 1, j + 1, 0], tab_texture[i + 1, j + 1, 1])
            glNormal3f(tab_vectors[i+1, j+1, 0], tab_vectors[i+1, j+1, 1], tab_vectors[i+1, j+1, 2])
            glVertex3f(tab[i + 1, j + 1, 0], tab[i + 1, j + 1, 1], tab[i + 1, j + 1, 2])

            glTexCoord2f(tab_texture[i, j+1, 0], tab_texture[i, j+1, 1])
            glNormal3f(tab_vectors[i, j + 1, 0], tab_vectors[i, j + 1, 1], tab_vectors[i, j + 1, 2])
            glVertex3f(tab[i, j + 1, 0], tab[i, j + 1, 1], tab[i, j + 1, 2])

            glEnd()

    glFlush()


def changeTexture():
    global active_texture

    if active_texture == 0: # aktywna domyslna tekstura
        glTexImage2D(
            GL_TEXTURE_2D, 0, 3, image2.size[0], image2.size[1], 0,
            GL_RGB, GL_UNSIGNED_BYTE, image2.tobytes("raw", "RGB", 0, -1)
        )
        active_texture = 1
    elif active_texture == 1: # aktywna druga tekstura
        glTexImage2D(
            GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0,
            GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1)
        )
        active_texture = 0


def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def keyboard_key_callback(window, key, scancode, action, mods):
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_SPACE and action == GLFW_PRESS:
        changeTexture()


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old

    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
