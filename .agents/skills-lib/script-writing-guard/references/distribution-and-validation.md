# Distribution And Validation

Use this reference only when the skill needs to be shared, moved to another machine, or archived as a portable package.

## What good packaging means

A portable skill package should:
- contain only the files needed for the skill to work;
- keep the folder structure intact;
- avoid broken links and stale references;
- avoid machine-specific hardcoded paths;
- fail early if the structure is invalid.

## Validation checklist

Before packaging, check:
- `SKILL.md` exists;
- YAML frontmatter contains `name` and `description`;
- the skill folder name matches the `name` value;
- local markdown links point to real files;
- no symlinks or reparse points are present;
- no obvious machine-specific paths are embedded in the skill content;
- packaged content is essential, not clutter.

## Packaging rule

Validate first, package second.

If validation fails, do not package the skill and do not treat the package as trustworthy.

## Helper scripts

From the skill folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-skill.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\package-skill.ps1
```

Optional custom output folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package-skill.ps1 -OutputDir C:\Temp\skill-dist
```

## When to avoid packaging

Do not package yet if:
- the skill is still changing heavily;
- trigger behavior is still unstable;
- references are incomplete;
- the skill still contains project-specific assumptions that should not travel.

## Practical note

Packaging is for portability, not for everyday use.

For normal local use, the unpackaged skill folder is enough.
