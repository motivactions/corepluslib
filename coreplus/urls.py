from coreplus import hooks

urlpatterns = [view_path_func() for view_path_func in hooks.get_hooks("COREPLUS_VIEWS")]
