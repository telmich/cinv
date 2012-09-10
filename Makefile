test:
	PYTHONPATH=$$PYTHONPATH:$$(pwd -P)/lib python3 -m sexy.test

githubpub:
	git push --mirror github

selfpub:
	git push --mirror

sanspub: selfpub githubpub
	git push --mirror sans

pub: selfpub githubpub sanspub
