#!/bin/sh
# MAke sure this is called from root level of repository
set -x
cookiecutter -f --no-input --config-file ./docs/vtki-binder-config.yml -o .. https://github.com/pyvista/cookiecutter-vtki-binder.git;
rm -rf ../vtki-examples/notebooks/;
cd ./docs/;
find ./examples -type f -name '*.ipynb' | cpio -p -d -v ../../vtki-examples/;
cd ../../vtki-examples/;
git init;
git add .;
git commit -m "$TRAVIS_BUILD_NUMBER : Autogenerated notebooks from Travis";
REMOTE="https://${GH_TOKEN}@github.com/pyvista/vtki-examples";
git config --global user.name "${GH_NAME}";
git config --global user.email "${GH_EMAIL}";
git remote add origin ${REMOTE};
git push -uf origin master;
cd ../vtki/
doctr deploy --built-docs ./docs/_build/html .;
set +x
