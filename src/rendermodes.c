/* 
 * This file is part of the Minecraft Overviewer.
 *
 * Minecraft Overviewer is free software: you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 *
 * Minecraft Overviewer is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with the Overviewer.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "overviewer.h"
#include <string.h>

/* list of all render modes, ending in NULL
   all of these will be available to the user, so DON'T include modes
   that are only useful as a base for other modes. */
static RenderModeInterface *render_modes[] = {
    &rendermode_normal,
    &rendermode_lighting,
    &rendermode_night,
    &rendermode_spawn,
    &rendermode_cave,
    NULL
};

/* decides which render mode to use */
RenderModeInterface *get_render_mode(RenderState *state) {
    unsigned int i;
    /* default: NULL --> an error */
    RenderModeInterface *iface = NULL;
    PyObject *rendermode_py = PyObject_GetAttrString(state->self, "rendermode");
    const char *rendermode = PyString_AsString(rendermode_py);
    
    for (i = 0; render_modes[i] != NULL; i++) {
        if (strcmp(render_modes[i]->name, rendermode) == 0) {
            iface = render_modes[i];
            break;
        }
    }
    
    Py_DECREF(rendermode_py);
    return iface;
}

/* bindings for python -- get all the rendermode names */
PyObject *get_render_modes(PyObject *self, PyObject *args) {
    PyObject *modes;
    unsigned int i;
    if (!PyArg_ParseTuple(args, ""))
        return NULL;
    
    modes = PyList_New(0);
    if (modes == NULL)
        return NULL;
    
    for (i = 0; render_modes[i] != NULL; i++) {
        PyObject *name = PyString_FromString(render_modes[i]->name);
        PyList_Append(modes, name);
        Py_DECREF(name);
    }
    
    return modes;
}

/* more bindings -- return info for a given rendermode name */
PyObject *get_render_mode_info(PyObject *self, PyObject *args) {
    const char* rendermode;
    PyObject *info;
    unsigned int i;
    if (!PyArg_ParseTuple(args, "s", &rendermode))
        return NULL;
    
    info = PyDict_New();
    if (info == NULL)
        return NULL;
    
    for (i = 0; render_modes[i] != NULL; i++) {
        if (strcmp(render_modes[i]->name, rendermode) == 0) {
            PyObject *tmp;
            
            tmp = PyString_FromString(render_modes[i]->name);
            PyDict_SetItemString(info, "name", tmp);
            Py_DECREF(tmp);
            
            tmp = PyString_FromString(render_modes[i]->description);
            PyDict_SetItemString(info, "description", tmp);
            Py_DECREF(tmp);
            
            return info;
        }
    }
    
    Py_DECREF(info);
    Py_RETURN_NONE;
}
