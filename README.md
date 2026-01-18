# Aris extension template

## Usage

### Initialization step
1. Create github repository from this template
2. Goto Actions -> Run Initialize project
3. Clone into your local
4. Run `git submodule update --remote --recursive` to retrieve latest code for aris
5. cd into aris-mc then run `./gradlew build -Penv=slave`
  >  This is mandatory due to [bug of loom+gradle-composite](https://github.com/FabricMC/fabric-loom/issues/685). This will create `aris-1.0.0.jar` artifact which makes loom possible to resolve metadata
6. Now RUN!

### Updating ARIS dependency
1. Run `git submodule update --remote --recursive`
2. (Optional but mandatory if update not applied) remove /.gradle directory to your root project
3. cd into aris-mc and run `./gradlew build -Penv=slave`
4. Now RUN!
