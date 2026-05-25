# Aris extension template

Starter template for Aris Minecraft mod extensions (Fabric + NeoForge via
Architectury). Dependencies — `me.ddayo:aris`, `me.ddayo:aris-fabric`,
`me.ddayo:aris-neoforge`, `me.ddayo:aris.luagen`, `me.ddayo:ap` — resolve
from the kei-managed Maven repo at <https://kei.ddayo.me/maven>.

## Initialization

1. Create a GitHub repository from this template.
2. **Actions → Initialize Project → Run workflow.** Fill in mod id,
   package, archives name, fabric/neoforge toggles, and which engine hooks
   you plan to extend. The workflow runs `setup.py` to rewrite the project
   accordingly, commits the result, and removes the bootstrap files
   (`setup.py`, `.github/workflows/init.yml`).
3. Clone the repo locally and run `./gradlew build`.

## Updating ARIS dependencies

The aris artifacts are published as SNAPSHOTs, so a normal `./gradlew build`
will only refetch them every 24 hours. To pick up a fresh publish:

```
./gradlew build --refresh-dependencies
```
