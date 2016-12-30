# python-awscli
* Provides a Python3 layer to AWS's CLI, all wrapped in a Docker
container
* This projects exists mostly just for fun
* There is almost no input checking. Trust is implicit as anyone who
can run this code already has full access to the bin/aws program. We
let AWS's code and permission structure do the real work.

## TODO
* `aws efs create-file-system`
* `aws efs create-mount-target`
