import os
import re
import shutil
import json

def get_env(key, default):
    return os.getenv(key, default)

def get_bool_env(key, default="false"):
    """Reads 'true'/'false' string from env and returns 'true'/'false' string for Gradle"""
    val = os.getenv(key, default).lower()
    return "true" if val == 'true' else "false"

def to_pascal_case(text):
    """Converts 'my-mod-project' to 'MyModProject'"""
    words = re.split(r'[^a-zA-Z0-9]', text)
    return "".join(word.capitalize() for word in words if word)

def update_gradle_properties(mod_id, package_name, archives_name, mod_description, mod_author, export_doc):
    print("📝 Updating gradle.properties...")

    # 1. Gather Flags
    enable_forge = os.getenv("ENABLE_FORGE", "true").lower() == 'true'
    enable_fabric = os.getenv("ENABLE_FABRIC", "true").lower() == 'true'

    # Determine enabled platforms string
    platforms = []
    if enable_fabric: platforms.append("fabric")
    if enable_forge: platforms.append("forge")
    platforms_str = ",".join(platforms) if platforms else "fabric"

    # Engine Flags
    engine_flags = {
        "extend_init_engine": get_bool_env("EXTEND_INIT_ENGINE"),
        "extend_in_game_engine": get_bool_env("EXTEND_IN_GAME_ENGINE"),
        "extend_client_init_engine": get_bool_env("EXTEND_CLIENT_INIT_ENGINE"),
        "extend_client_main_engine": get_bool_env("EXTEND_CLIENT_MAIN_ENGINE"),
        "extend_client_in_game_engine": get_bool_env("EXTEND_CLIENT_IN_GAME_ENGINE"),
    }

    # 2. Prepare New Content
    marker = "# --- Auto-Generated Properties ---"
    new_props_block = [
        f"{marker}\n",
        f"maven_group={package_name}\n",
        f"mod_id={mod_id}\n",
        f"archives_name={archives_name}\n",
        f"mod_name={archives_name}\n",
        f"enabled_platforms={platforms_str}\n",
        f"export_doc_on_build={export_doc}\n",
        f"mod_description={mod_description}\n",
        f"mod_authors={mod_author}\n",
    ]

    for key, val in engine_flags.items():
        new_props_block.append(f"{key}={val}\n")

    # 3. Read Existing & Truncate
    gradle_props_path = "gradle.properties"
    final_lines = []

    if os.path.exists(gradle_props_path):
        with open(gradle_props_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Keep lines only until the marker is found
        for line in lines:
            if marker in line:
                break
            final_lines.append(line)

        # Ensure the manual section ends with a newline before we append
        if final_lines and not final_lines[-1].endswith('\n'):
            final_lines[-1] += '\n'

        # Add a cosmetic newline between manual and auto sections if there is manual content
        if final_lines and final_lines[-1].strip() != "":
            final_lines.append("\n")

    # 4. Write Complete File (Manual + New Auto)
    with open(gradle_props_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines + new_props_block)

    print("✅ gradle.properties updated.")

def update_settings_gradle(archives_name):
    print("⚙️ Updating settings.gradle...")

    enable_forge = os.getenv("ENABLE_FORGE", "true").lower() == 'true'
    enable_fabric = os.getenv("ENABLE_FABRIC", "true").lower() == 'true'

    settings_path = "settings.gradle"
    marker = "// --- Auto-Generated Settings ---" # Using // for Groovy syntax compatibility

    # Default header to use ONLY if the file doesn't exist yet
    default_header = """pluginManagement {
    repositories {
        maven { url "https://maven.fabricmc.net/" }
        maven { url "https://maven.architectury.dev/" }
        maven { url "https://files.minecraftforge.net/maven/" }
        gradlePluginPortal()
    }
    plugins {
        id 'com.google.devtools.ksp' version '2.1.20-2.0.0'
    }
}
plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}
"""

    # 1. Read Existing & Truncate
    final_lines = []

    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if marker in line:
                break
            final_lines.append(line)

        # Ensure spacing
        if final_lines and not final_lines[-1].endswith('\n'):
            final_lines[-1] += '\n'

        if final_lines and final_lines[-1].strip() != "":
            final_lines.append("\n")
    else:
        # If file missing, create with default header
        final_lines = [default_header + "\n"]

    # 2. Build Auto-Generated Content
    auto_content = f"{marker}\n"
    auto_content += f"rootProject.name = '{archives_name}'\n\n"

    auto_content += "includeBuild('aris-mc') {\n"
    auto_content += "    dependencySubstitution {\n"
    auto_content += "        substitute module('me.ddayo:aris-common') using project(':common')\n"

    if enable_fabric:
        auto_content += "        substitute module('me.ddayo:aris-fabric') using project(':fabric')\n"

    if enable_forge:
        auto_content += "        substitute module('me.ddayo:aris-forge') using project(':forge')\n"

    auto_content += "    }\n"
    auto_content += "}\n\n"

    auto_content += "include 'common'\n"

    if enable_fabric:
        auto_content += "include 'fabric'\n"

    if enable_forge:
        auto_content += "include 'forge'\n"

    # 3. Write File
    with open(settings_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)
        f.write(auto_content)

    print("✅ settings.gradle updated.")

def update_common_gradle(package_name, export_doc):
    print("🐘 Updating common/build.gradle...")

    gradle_path = "common/build.gradle"
    marker = "// --- Auto-Generated Settings ---"

    final_lines = []
    if os.path.exists(gradle_path):
        with open(gradle_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if marker in line:
                break
            final_lines.append(line)

        if final_lines and not final_lines[-1].endswith('\n'):
            final_lines[-1] += '\n'
        if final_lines and final_lines[-1].strip() != "":
            final_lines.append("\n")

    # Prepare the KSP block
    ksp_block = f"{marker}\n"
    ksp_block += "ksp {\n"
    ksp_block += f'    arg("package_name", "{package_name}.lua.glue")\n'
    ksp_block += f'    arg("export_doc", "{export_doc}")\n'
    ksp_block += "}\n"

    with open(gradle_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)
        f.write(ksp_block)

    print("✅ common/build.gradle updated.")

def create_kotlin_templates(package_name, mod_id):
    print("🛠️ Generating Kotlin Template Files...")

    # Prepare paths and names
    package_path = package_name.replace('.', '/')
    pascal_mod_id = to_pascal_case(mod_id)

    # Define file structures
    # (path_prefix, sub_path, class_name, content)
    templates = [
        # 1. Common Main
        ("common/src/main/kotlin", f"{package_path}/{mod_id}", f"{pascal_mod_id}.kt",
         f"package {package_name}.{mod_id}\n\nobject {pascal_mod_id} {{\n    const val MOD_ID = \"{mod_id}\"\n    fun init() {{}}\n}}"),

        # 2. Common Client
        ("common/src/main/kotlin", f"{package_path}/{mod_id}/client", f"{pascal_mod_id}Client.kt",
         f"package {package_name}.{mod_id}.client\n\nobject {pascal_mod_id}Client {{\n    fun init() {{}}\n}}"),

        # 3. Fabric Main
        ("fabric/src/main/kotlin", f"{package_path}/{mod_id}/fabric", f"{pascal_mod_id}Fabric.kt",
         f"package {package_name}.{mod_id}.fabric\n\nimport {package_name}.{mod_id}.{pascal_mod_id}\n\nobject {pascal_mod_id}Fabric {{\n    fun init() {{\n        {pascal_mod_id}.init()\n    }}\n}}"),

        # 4. Fabric Client
        ("fabric/src/main/kotlin", f"{package_path}/{mod_id}/client/fabric", f"{pascal_mod_id}FabricClient.kt",
         f"package {package_name}.{mod_id}.client.fabric\n\nimport {package_name}.{mod_id}.client.{pascal_mod_id}Client\n\nobject {pascal_mod_id}FabricClient {{\n    fun init() {{\n        {pascal_mod_id}Client.init()\n    }}\n}}"),

        # 5. Forge Main
        ("forge/src/main/kotlin", f"{package_path}/{mod_id}/forge", f"{pascal_mod_id}Forge.kt",
         f"package {package_name}.{mod_id}.forge\n\nimport {package_name}.{mod_id}.{pascal_mod_id}\nimport net.minecraftforge.fml.common.Mod\n\n@Mod({pascal_mod_id}.MOD_ID)\nclass {pascal_mod_id}Forge {{\n    init {{\n        {pascal_mod_id}.init()\n    }}\n}}"),

        # 6. Forge Client
        ("forge/src/main/kotlin", f"{package_path}/{mod_id}/client/forge", f"{pascal_mod_id}ForgeClient.kt",
         f"package {package_name}.{mod_id}.client.forge\n\nimport {package_name}.{mod_id}.client.{pascal_mod_id}Client\n\nobject {pascal_mod_id}ForgeClient {{\n    fun init() {{\n        {pascal_mod_id}Client.init()\n    }}\n}}"),
    ]

    enable_forge = os.getenv("ENABLE_FORGE", "true").lower() == 'true'
    enable_fabric = os.getenv("ENABLE_FABRIC", "true").lower() == 'true'

    for root, sub, filename, content in templates:
        # Skip if platform is disabled
        if "fabric" in root and not enable_fabric: continue
        if "forge" in root and not enable_forge: continue

        full_dir = os.path.join(root, sub)
        os.makedirs(full_dir, exist_ok=True)

        with open(os.path.join(full_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   -> Created {filename}")

def create_engine_extensions(package_name, mod_id):
    print("⚙️ Generating Engine Extensions...")

    package_path = package_name.replace('.', '/')
    pascal_mod_id = to_pascal_case(mod_id)
    enable_forge = os.getenv("ENABLE_FORGE", "true").lower() == 'true'
    enable_fabric = os.getenv("ENABLE_FABRIC", "true").lower() == 'true'

    # Mapping of ENV keys to their specific configurations
    # (EnvKey, FolderName, ClassSuffix, EngineType, IsClient)
    engine_configs = [
        ("EXTEND_INIT_ENGINE", "engine", "InitFunction", "InitEngine", False),
        ("EXTEND_IN_GAME_ENGINE", "engine", "InGameFunction", "InGameEngine", False),
        ("EXTEND_CLIENT_INIT_ENGINE", "engine/client", "ClientInitFunction", "ClientInitEngine", True),
        ("EXTEND_CLIENT_MAIN_ENGINE", "engine/client", "ClientMainFunction", "ClientMainEngine", True),
        ("EXTEND_CLIENT_IN_GAME_ENGINE", "engine/client", "ClientInGameFunction", "ClientInGameEngine", True),
    ]

    for env_key, folder, suffix, engine_type, is_client in engine_configs:
        if os.getenv(env_key, "false").lower() != "true":
            continue

        provider_name = f"{pascal_mod_id}{suffix}"
        provider_const = f"{pascal_mod_id}{suffix.replace('Function', 'Provider')}"
        generated_class = f"{pascal_mod_id}{suffix.replace('Function', 'Provider')}Generated"

        # 1. Common Provider
        common_dir = f"common/src/main/kotlin/{package_path}/{mod_id}/{folder}"
        os.makedirs(common_dir, exist_ok=True)
        with open(f"{common_dir}/{provider_name}.kt", "w") as f:
            f.write(f"""package {package_name}.{mod_id}.{folder.replace('/', '.')}

import me.ddayo.aris.luagen.LuaFunction
import me.ddayo.aris.luagen.LuaProvider

@LuaProvider({provider_name}.PROVIDER)
object {provider_name} {{
    const val PROVIDER = "{provider_const}"
}}""")

        # 2. Fabric Extension
        if enable_fabric:
            fab_dir = f"fabric/src/main/kotlin/{package_path}/{mod_id}/{folder}/fabric"
            os.makedirs(fab_dir, exist_ok=True)
            with open(f"{fab_dir}/{pascal_mod_id}Fabric{suffix}Extension.kt", "w") as f:
                f.write(f"""package {package_name}.{mod_id}.{folder.replace('/', '.')}.fabric

import me.ddayo.aris.engine.EngineInitializer
import me.ddayo.aris.engine.{engine_type}
import {package_name}.{mod_id}.lua.glue.{generated_class}

class {pascal_mod_id}Fabric{suffix}Extension : EngineInitializer<{engine_type}> {{
    override fun initLua(engine: {engine_type}) {{
        {generated_class}.initEngine(engine)
    }}
}}""")

    print("✅ Engine extensions generated.")

def update_forge_main(package_name, mod_id):
    """Specific handler for Forge main class to inject the MOD_BUS listeners"""
    pascal_mod_id = to_pascal_case(mod_id)
    path = f"forge/src/main/kotlin/{package_name.replace('.', '/')}/{mod_id}/forge/{pascal_mod_id}Forge.kt"

    if not os.path.exists(path): return

    engine_configs = [
        ("EXTEND_INIT_ENGINE", "Init"),
        ("EXTEND_IN_GAME_ENGINE", "InGame"),
        ("EXTEND_CLIENT_INIT_ENGINE", "ClientInit"),
        ("EXTEND_CLIENT_MAIN_ENGINE", "ClientMain"),
        ("EXTEND_CLIENT_IN_GAME_ENGINE", "ClientInGame"),
    ]

    listener_blocks = ""
    for env_key, suffix in engine_configs:
        if os.getenv(env_key, "false").lower() == "true":
            generated_class = f"{pascal_mod_id}{suffix}ProviderGenerated"
            listener_blocks += f"""
        MOD_BUS.addListener {{ it: FMLConstructModEvent ->
            ArisForge.initExtensions.add {{
                {generated_class}.initEngine(it)
            }}
        }}"""

    if listener_blocks:
        with open(path, "r") as f: content = f.read()
        # Inject into the init block
        new_content = content.replace("init {", "init {" + listener_blocks)
        with open(path, "w") as f: f.write(new_content)

def update_fabric_mod_json(package_name, mod_id):
    print("🧵 Injecting hardcoded entrypoints into fabric.mod.json...")

    path = "fabric/src/main/resources/fabric.mod.json"
    pascal_mod_id = to_pascal_case(mod_id)
    base_pkg = f"{package_name}.{mod_id}"

    # 1. Build the actual Entrypoints Dictionary
    entrypoints = {
        "main": [f"{base_pkg}.fabric.{pascal_mod_id}Fabric::init"],
        "client": [f"{base_pkg}.client.fabric.{pascal_mod_id}FabricClient::init"]
    }

    # Conditional Engine Entrypoints based on ENV
    configs = [
        ("EXTEND_INIT_ENGINE", "aris-init", f"{base_pkg}.engine.fabric.{pascal_mod_id}FabricInitFunctionExtension"),
        ("EXTEND_CLIENT_INIT_ENGINE", "aris-client-init", f"{base_pkg}.engine.client.fabric.{pascal_mod_id}FabricClientInitFunctionExtension"),
        ("EXTEND_CLIENT_MAIN_ENGINE", "aris-client", f"{base_pkg}.engine.client.fabric.{pascal_mod_id}FabricClientMainFunctionExtension"),
        ("EXTEND_IN_GAME_ENGINE", "aris-game", f"{base_pkg}.engine.fabric.{pascal_mod_id}FabricInGameFunctionExtension"),
        ("EXTEND_CLIENT_IN_GAME_ENGINE", "aris-client-game", f"{base_pkg}.engine.client.fabric.{pascal_mod_id}FabricClientInGameFunctionExtension"),
    ]

    for env_key, entry_key, class_path in configs:
        if os.getenv(env_key, "false").lower() == "true":
            entrypoints[entry_key] = [class_path]

    # 2. Load existing or create new
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {
            "schemaVersion": 1,
            "id": mod_id,
            "version": "${version}",
            "name": mod_id
        }

    # 3. Inject the dictionary directly
    data["entrypoints"] = entrypoints

    # 4. Write back
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ fabric.mod.json updated with {len(entrypoints)} entrypoints.")

def cleanup_unused_platforms():
    print("🧹 Cleaning up unused platforms...")

    enable_forge = os.getenv("ENABLE_FORGE", "true").lower() == 'true'
    enable_fabric = os.getenv("ENABLE_FABRIC", "true").lower() == 'true'

    if not enable_fabric:
        if os.path.exists("fabric"):
            shutil.rmtree("fabric")
            print("   -> Removed fabric/ directory")

    if not enable_forge:
        if os.path.exists("forge"):
            shutil.rmtree("forge")
            print("   -> Removed forge/ directory")

def main():
    print("🚀 Starting Project Setup...")

    # Load Main Variables
    PROJECT_NAME = get_env("PROJECT_NAME", "Aris Extension Project")
    PACKAGE_NAME = get_env("PACKAGE_NAME", "com.example.app")
    ARCHIVES_NAME = get_env("ARCHIVES_NAME", "aris-extension")
    MOD_DESCRIPTION = get_env("MOD_DESCRIPTION", "Aris Extension Project")
    MOD_ID = get_env("MOD_ID", "arisextension")
    MOD_AUTHOR = get_env("MOD_AUTHOR", "Dayo")
    EXPORT_DOC = get_bool_env("EXPORT_DOC_ON_BUILD")

    print(f"Title: {PROJECT_NAME}")
    print(f"Package: {PACKAGE_NAME}")

    # Run Tasks
    update_gradle_properties(MOD_ID, PACKAGE_NAME, ARCHIVES_NAME, MOD_DESCRIPTION, MOD_AUTHOR, EXPORT_DOC)
    update_settings_gradle(ARCHIVES_NAME)
    update_common_gradle(PACKAGE_NAME, EXPORT_DOC)
    create_kotlin_templates(PACKAGE_NAME, MOD_ID)
    create_engine_extensions(PACKAGE_NAME, MOD_ID)
    update_fabric_mod_json(PACKAGE_NAME, MOD_ID)
    update_forge_main(PACKAGE_NAME, MOD_ID)
    resource_dir = "common/src/main/resources"
    os.rename(os.path.join(resource_dir, "aris_ext.mixins.json"), os.path.join(resource_dir, f"{MOD_ID}.mixins.json"))
    cleanup_unused_platforms()

    print("🎉 Setup complete!")

if __name__ == "__main__":
    main()