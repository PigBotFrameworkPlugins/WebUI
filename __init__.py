import os

from pbf.utils import MetaData, Utils
from pbf.controller.Data import Event
from pbf.utils.Register import Command
from pbf.setup import logger, pluginsManager

try:
    import psutil
    import git
except ImportError:
    Utils.installPackage("psutil")
    Utils.installPackage("GitPython")

require = pluginsManager.require

meta_data = MetaData(
    name="Web UI",
    version="0.0.1",
    versionCode=1,
    description="A web ui for PBF Next",
    author="XzyStudio",
    license="MIT",
    keywords=["pbf", "plugin", "web", "ui"],
    readme="""
# Web UI
这是PBF Next的Web UI插件，借助Fastapi与Jinja2提供一个便捷的Web管理面板

## 使用
仅需要访问`{your_server}/web/`即可控制面板！
    """
)

def _enter():
    from fastapi.templating import Jinja2Templates
    from pbf.setup import pluginsManager, ListenerManager
    from pbf.utils import Path
    from pbf.driver.Fastapi import app
    from fastapi import Request
    import pbf
    from git import Repo
    import shutil
    import platform
    from pbf import config

    templates = Jinja2Templates(directory=f"{os.path.dirname(__file__)}/templates")

    @app.get("/web/api/sys_info", tags=["Web UI"])
    async def sys_info(request: Request):
        return [psutil.cpu_percent(), psutil.virtual_memory().percent, psutil.disk_usage("/").percent]
    
    @app.get("/web/api/get_plugin", tags=["Web UI"])
    async def get_plugin(plugin_id: str):
        data = pluginsManager.getAllPlugins().get(plugin_id, {})
        if data:
            data["readme"] = data["readme"].strip()
            data["listeners"] = ListenerManager.get_listeners_by_plugin_name(plugin_id)
        return data
    
    @app.get("/web/api/install_plugin", tags=["Web UI"])
    async def install_plugin(repo_url: str, reinstall: bool = False):
        plugin = repo_url.replace('.git', '').split('/')[-1]
        try:
            if reinstall:
                try:
                    pluginsManager.disable(plugin)
                    shutil.rmtree(f"{Path.replace(config.plugins_directory)}/{plugin}")
                except Exception as e:
                    pass
            Repo.clone_from(repo_url, f"{Path.replace(config.plugins_directory)}/{plugin}")
        except Exception as e:
            return {"error": str(e)}
        pluginsManager.loadPlugin(plugin)

    @app.get("/web/", tags=["Web UI"])
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={
                "PBFInfo": {
                    "版本": {
                        "版本": pbf.version,
                        "版本号": pbf.version_code,
                    },
                    "日志": {
                        "日志目录": config.logs_directory,
                        "日志等级": config.logs_level,
                        "日志格式": config.logs_format,
                    },
                    "插件": {
                        "插件目录": config.plugins_directory,
                        "禁用的插件": config.plugins_disabled,
                    },
                    "SQL": {
                        "SQL Driver": config.sql_driver,
                    },
                    "OneBot Connect": {
                        "Uri": config.ob_uri,
                        "Version": config.ob_version,
                        "Access Token": config.ob_access_token,
                    }
                },
                "SystemInfo": {
                    "操作系统及版本信息": platform.platform(),
                    "获取系统版本号": platform.version(),
                    "获取系统名称": platform.system(),
                    "系统位数": platform.architecture(),
                    "计算机类型": platform.machine(),
                    "计算机名称": platform.node(),
                    "处理器类型": platform.processor(),
                },
                "WebUIInfo": {
                    "meta_data": meta_data
                }
            }
        )

    @app.get("/web/plugins/", tags=["Web UI"])
    async def plugins(request: Request, q:str = None):
        data = pluginsManager.getAllPlugins()
        plugins = {}
        if q:
            for k, v in data.items():
                if q in v.get("name") or q in k:
                    plugins[k] = v
        else:
            plugins = data
        return templates.TemplateResponse(
            request=request, name="plugins.html",
            context={
                "plugins": plugins,
                "q": q
            }
        )

    @app.get("/web/listeners/", tags=["Web UI"])
    async def listeners(request: Request, q:str = None):
        return templates.TemplateResponse(
            request=request, name="listeners.html",
            context={
                "listeners": {
                    "Command": ListenerManager.get_listeners_by_type("command"),
                    "Message": ListenerManager.get_listeners_by_type("message"),
                    "Notice": ListenerManager.get_listeners_by_type("notice"),
                    "Request": ListenerManager.get_listeners_by_type("request"),
                    "Meta": ListenerManager.get_listeners_by_type("meta"),
                }
            }
        )
    
    @app.get("/web/ob/", tags=["Web UI"])
    async def ob(request: Request, q:str = None):
        return templates.TemplateResponse(
            request=request, name="ob.html",
            context={
                
            }
        )
    
    @app.get("/web/ob/online", tags=["Web UI"])
    async def ob_online(request: Request, q:str = None):
        return templates.TemplateResponse(
            request=request, name="ob_online.html",
            context={
                
            }
        )
