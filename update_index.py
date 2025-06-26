import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

REPO_USER = "signorzhao"
REPO_NAME = "reapack_repo"
PLUGIN_BASENAMES = [
    "reaper_enz_ReaperTools.dll",   # Windows
    "reaper_enz_ReaperTools.dylib", # macOS
    "reaper_enz_ReaperTools.so",    # Linux
]

PLATFORM_MAP = {
    "reaper_enz_ReaperTools.dll": ("windows", "x64"),
    "reaper_enz_ReaperTools.dylib": ("macos", "x64"),
    "reaper_enz_ReaperTools.so": ("linux", "x64"),
}

def find_versions(base_dir="releases"):
    """Scan releases/vX.Y.Z directories for plugin files"""
    versions = []
    for item in os.listdir(base_dir):
        if item.startswith("v"):
            for plugin_name in PLUGIN_BASENAMES:
                if os.path.exists(f"{base_dir}/{item}/{plugin_name}"):
                    versions.append(item)
                    break
    return sorted(versions, key=lambda s: list(map(int, s[1:].split('.'))))

def create_index(versions):
    """Create the index.xml structure"""
    root = Element("reapack", version="1")
    category = SubElement(root, "category", name="MyPlugin")
    for v in versions:
        version_num = v[1:]  # v1.0.0 -> 1.0.0
        for plugin_name in PLUGIN_BASENAMES:
            plugin_path = f"releases/{v}/{plugin_name}"
            if not os.path.exists(plugin_path):
                continue
            os_name, arch = PLATFORM_MAP[plugin_name]
            reapack = SubElement(category, "reapack",
                                 name=plugin_name,
                                 version=version_num,
                                 type="extension")
            SubElement(reapack, "description").text = "My REAPER C++ Extension Plugin"
            SubElement(reapack, "source",
                       file=f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/main/releases/{v}/{plugin_name}")
            compatibility = SubElement(reapack, "compatibility")
            SubElement(compatibility, "os").text = os_name
            SubElement(compatibility, "arch").text = arch

    xml_string = tostring(root, 'utf-8')
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    versions = find_versions()
    xml_contents = create_index(versions)
    with open("index.xml", "w", encoding="utf-8") as f:
        f.write(xml_contents)
    print(f"✅ index.xml updated with versions: {', '.join(versions)}.") 