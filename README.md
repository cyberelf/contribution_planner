# GitHub Contribution Planner

GitHub Contribution Planner is a command-line tool for planning your GitHub contributions. You can use it to generate a contribution matrix, which can be used to plan your commits.

![calendar](calendar.png)

## Usage

You can use this tool with the following command:

```bash
python plan.py <text> [-y YEAR] [--font FONT] [-c] [-o] [-s]
```

Here's what the arguments mean:

* text: The text you want to plan.
* -y, --year YEAR: The year you want to plan for.
* --font FONT: The font you want to use.
* -c, --commit-level: Use commit level colors.
* -o, --save-icalendar: Save to an iCalendar file.
* -s, --save-image: Display the image.

Note: You need to choose at least one of --save-icalendar and --save-image.

For example, if you want to plan a text called "Hello" for the year 2024 and save it to an iCalendar file, you can use the following command:

```bash
python plan.py Hello -y 2024 -c -s -o 
```

### Default Values

If you don't provide the --font argument, the default font used is "font/DejaVuSans-Bold.ttf".

If you don't provide the -c argument, the default mode used is to generate commit plan without commit levels.
