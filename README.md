getRepos
========

Two entries, one from claude one from Gemini.  I'd written this before for my
work github, so I was familiar with the API wrinkles.  The only mistake that
the AIs made (both of them) was to add an extra string "token" between
the Authorization: and the token value for the API auth.

I use this as I have a varying number of compute end nodes that I use, so
this cloning script makes it easier to switch to a new one.

Also, when I get curious about someone, I can add them to users.txt
and clone all their repos.

--Chris