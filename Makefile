opub:
	git push --tags
	git push --all

# Nicos version of merge latest changes from Steven
merge:
	git pull sans next

# Nicos version of public pushes to two destinations
pub: opub merge
	git push --tags sans
	git push --all sans
