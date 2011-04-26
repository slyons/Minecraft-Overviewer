"""
    environment.py
    
    Build environment for Overviewer.
"""

import sys
import os.path
import logging
from configParser import ConfigOptionParser

class BuildEnvironment(object):
    
    def __init__(self):
        self._build_hooks = {}
        self._default_hooks = {}
        self._steps = []
        self._properties = {  }
        self._currentStep = None
        self._envlog = logging.getLogger("BuildEnv")
        self.log = logging.getLogger("Prebuild")
        
    def add_hook(self, build_step, func):
        if not callable(func):
            raise RuntimeError("%r is not a callable object!" % func)
        if build_step not in self._steps:
            self._envlog.warning("'%s' is not a build step!" % build_step)
        hooks = self._build_hooks.get(build_step, [])
        hooks.append(func)
        
    def add_step(self, build_step, before_step=None, after_step=None, hook=None):
        # Adds a build step to the list with an optional default hook
        if build_step in self._steps:
            raise ValueError("%s is already a build step!" % build_step)
        
        if before_step and before_step in self._steps:
            before_index = self._steps.index(before_step)
        else:
            before_index = None
        if after_step and after_step in self._steps:
            after_index = self._steps.index(after_step)
        else:
            after_index = None
        
        if before_index and after_index and (after_index > before_index):
            raise ValueError("Cannot place %(build_step)s before %(before_step)s and after %(after_step)s due to ordering." % locals())
            
        if before_index:
            self._steps.insert(before_index, build_step)
        elif after_index:
            self._steps.insert(after_index+1, build_step)
        else:
            self._steps.append(build_step)
            self._build_hooks[build_step] = []
        self._envlog.debug("Creating step %r at position %d" % (build_step, self._steps.index(build_step)))
            
        if hook:
            self._default_hooks[build_step] = hook
            self._envlog.debug("Step %r has default hook %r" % (build_step, hook))
            
    def __iter__(self):
        for (index, step) in enumerate(self._steps):
            self._envlog.info("Step %d: %r" % (index+1, step))
            self._currentStep = step
            self._properties["step"] = step
            self._properties["step_index"] = self._steps.index(step)
            
            dhooks = self._default_hooks.get(step, None)
            if callable(dhooks) or not dhooks:
                (before, after) = (dhooks, None)
            elif isinstance(dhooks, tuple):
                (before, after) = dhooks
                
            if before:
                self._envlog.debug('Calling prehook %s' % before.func_name)
                self.log.name = before.func_name
                before(self._properties)
                self._envlog.debug("Prehook finished.")
                
            for hook in self._build_hooks.get(step, []):
                self._envlog.debug("Caling hook %s" % hook.func_name)
                self.log.name = hook.func_name
                hook(self._properties)
                self._envlog.debug("Hook done.")
                
            if after:
                self._envlog.debug("Calling posthook %s" % after.func_name)
                self.log.name = after.func_name
                after(self._properties)
                self._envlog.debug("Posthook finished.")
            
            yield self._properties
            
    def __len__(self):
        return len(self._steps)
        
    def __get__(self, key):
        return self._properties.get(key, None) or object.__get__(self, key)
        
    def __set__(self, key, value):
        if key in dir(self):
            object.__set__(self, key, value)
        else:
            self._properties.set(key, value)
            
    def __setitem__(self, key, value):
        self._properties[key] = value
        
    def __getitem__(self, key):
        return self._properties.get(key)
        
    def __contains__(self, key):
        return key in self._properties
        
    def __delitem__(self, key):
        del self._properties[key]
            
"""
    Example usage:

    def build_environment(build_env):
        env.log.info("This is where we would do something before other hooks")
        build_env["before"] = True

    def envhook(build_env):
        env.log.info("")
        env["aheadley"] = "jerk"

    def validate_environment(build_env):
        env.log.info("This is after all other hooks for this step.")
        env["after"] = True

    logging.basicConfig(level=logging.INFO)

    env = BuildEnvironment()
    env.add_step("environment", hook=(build_environment, validate_environment))
    env.add_hook("environment", envhook)
    for s in env:
        print s
"""
