import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import datetime

REPO_USER = "signorzhao"
REPO_NAME = "reapack_repo"
PLUGIN_BASENAMES = [
    "reaper_enz_ReaperTools.dll",   # Windows
    "reaper_enz_ReaperTools.dylib", # macOS
    "reaper_enz_ReaperTools.so",    # Linux
]

PLATFORM_MAP = {
    "reaper_enz_ReaperTools.dll": "win64",
    "reaper_enz_ReaperTools.dylib": "darwin",
    "reaper_enz_ReaperTools.so": "linux",
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
    """Create the index.xml structure following ReaPack standard"""
    root = Element("index", version="1", name="ENZ ReaperTools", commit="main")
    
    category = SubElement(root, "category", name="Extensions")
    
    # Create one reapack element for the plugin
    reapack = SubElement(category, "reapack", 
                        name="reaper_enz_ReaperTools.ext", 
                        type="extension", 
                        desc="ENZ ReaperTools")
    
    # Add metadata
    metadata = SubElement(reapack, "metadata")
    description = SubElement(metadata, "description")
    description.text = "ENZ ReaperTools - REAPER C++ Extension Plugin"
    
    # Add versions
    for v in versions:
        version_num = v[1:]  # v1.0.0 -> 1.0.0
        version_elem = SubElement(reapack, "version", 
                                 name=version_num, 
                                 author="ENZ", 
                                 time=datetime.datetime.now().isoformat() + "Z")
        
        # Add sources for each platform
        for plugin_name in PLUGIN_BASENAMES:
            plugin_path = f"releases/{v}/{plugin_name}"
            if os.path.exists(plugin_path):
                platform = PLATFORM_MAP[plugin_name]
                source = SubElement(version_elem, "source", 
                                   platform=platform, 
                                   file=plugin_name)
                source.text = f"https://raw.githubusercontent.com/{REPO_USER}/{REPO_NAME}/main/releases/{v}/{plugin_name}"

    xml_string = tostring(root, 'utf-8')
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    versions = find_versions()
    xml_contents = create_index(versions)
    with open("index.xml", "w", encoding="utf-8") as f:
        f.write(xml_contents)
    print(f"✅ index.xml updated with versions: {', '.join(versions)}.")
