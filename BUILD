python_requirements()

INBOX_SPECIFIC = {
    "flanker": "0.4.22-inbox",
    "IMAPClient": "0.11.101-inbox",
    "talon": "1.0.2-inbox",
    "PyNaCl": "0.3.0-inbox",
}

python_requirement_library(name = "inbox-specific",
                           requirements = [
                               python_requirement("%s==%s" % (pkg, vers)) \
                               for pkg,vers in INBOX_SPECIFIC.items()
                           ])

def python_requirement_dependencies():
    result = []
    with open("requirements.txt", "rb") as f:
        for line in f.readlines():
            if not line or line.startswith("#") or line.startswith("git"):
                continue

            result.append(":%s" % line.split("==")[0])

    return result

python_library(name = "inbox", sources = rglobs("inbox/*.py"),
               resources = rglobs("inbox/*.html", "inbox/*.css",
                                  "inbox/*.js", "inbox/*.txt"),
               dependencies = [":inbox-specific"] + \
               python_requirement_dependencies())

python_tests(name = "inbox-test", sources = rglobs("tests/*.py"),
             dependencies = [":inbox"])

python_binary(name = "api", source = "bin/inbox_api.py",
              dependencies = [":inbox"])
