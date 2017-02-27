# Full build-test-deploy makefile

This example demonstrates how the `Makefile` and `settings.py` are used
setup a CI/CD workflow which does the following:
  - pushes tags to the git repo
  - pushes new docker images to docker hub
  - instructs the production environment to update with latest code

# settings.py (mini-ci)
Remember, this file defines environment variables which are injected into
the container that runs the build. The only hard requirement is to set
`GIT_REPO`. All other environment variables are on you and completely 
optional.

However, in this example we define additional environment variables which
are used to configure and deploy to a dokku server.

# .env (mini-ci)
This is the file that docker-compose will consume to pull in SSH keys
for access to remote git repos and deployment systems. See comments in
the env.sample of the root folder of this project for more information.

# Makefile (in your project)
The `Makefile` will have access to the environment variables that come
from your project's configuration in settings.py. See the comments in the
Makefile sourcecode to see how they are used.

Please take note how this Makefile uses environment variables from 
`settings.py` which are used in naming and tagging docker images as
well as instructing the production environment (dokku server) to update
code with new docker images.

**REQUIREMENT**: You must define the `ci-deploy` target in your makefile
for the runner to do its job. This is a hard-coded requirement at the
moment.
