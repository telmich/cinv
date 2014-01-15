testedpub: test pub

test:
	PYTHONPATH=$$PYTHONPATH:$$(pwd -P)/lib python3 -m sexy.test

githubpub:
	git push --mirror github

selfpub:
	git push --mirror

pub: selfpub githubpub
