opub:
	git push --tags
	git push --all

# Nicos version of public pushes to two destinations
pub: opub
	git push --tags sans
	git push --all sans
