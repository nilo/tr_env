# tr_env
Terraform Environments

Psss hey! 
Are you looking for a way to run pieces of your Terraform code to a specific env?
Or you want to stay doing this: `count = "${var.environment == "prod" ? 1 : 0}"` ?

With `tr_env` you can tag with `#EXCLUDE:` your resources to exclude for a specific environment:

Example:

```HCL
terraform {
  backend "s3" {
    key = "terraform.state"

    # Production Env
    /* bucket   = "MYBUCKET-prod" */
    /* region   = "us-east-1" */

    # Staging Env
    /* bucket   = "MYBUCKET-stag" */
    /* region   = "us-east-1" */
    
    # Dev Env
    bucket   = "MYBUCKET-dev"
    region   = "us-east-1"

    # CI Env
    /* bucket   = "MYBUCKET-CI" */
    /* region   = "us-east-1" */
  }
}

#EXCLUDE: stag,dev,ci
resource "aws_instance" "gitlab" {

  ami           = "${lookup(var.gitlab, "ami.${var.environment}")}"
  instance_type = "${lookup(var.gitlab, "instance_type.${var.environment}")}"

  subnet_id = "${var.subnets_private[0]}"
  key_name  = "${aws_key_pair.gitlab.key_name}"

  vpc_security_group_ids = [
    "${aws_security_group.gitlab.id}",
  ]

	depends_on = ["aws_security_group.gitlab"]

  tags = "${merge(map("Name", "Gitlab-${var.environment}"), var.tags)}"
}

```
And when you ran:
`python tr_env.py -e dev -t "terraform plan"`
It will ignore all resources tagged to be exclude on dev. It works with modules too!

### How it works:
It just comment all tagged regions, run your `terraform` command and then uncomment it. Simple like that.
Remember to separate you envs into diferent state files!

:D
