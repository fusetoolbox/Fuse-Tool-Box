import pkgutil
import os

# 递归收集所有模块名（用于 PyInstaller 的 hiddenimports）
def get_all_modules(package_name, package_path):
    modules = []
    for loader, module_name, is_pkg in pkgutil.iter_modules([package_path]):
        full_name = f"{package_name}.{module_name}"
        if is_pkg:
            # 递归子包
            sub_path = os.path.join(package_path, module_name)
            modules.extend(get_all_modules(full_name, sub_path))
        else:
            modules.append(full_name)
    return modules

# 将结果暴露给 PyInstaller 或其他脚本
__all__ = get_all_modules(__name__, os.path.dirname(__file__))