# TXTBuilder

TXTBuilder is a parser that works like a mini programming-language that can be used to generate social media post descriptions for YouTube or Instagram, text art or any Unicode text document that obeys a specific pattern.

Another use case is generating prompts for AI tools like Midjourney.

<br>

## How to run

Download the package, create your file `commands.txt`, create the following script that imports TXTB and run it:

```python
import sys
import txtbuilder

INPUT_NAME = "commands.txt"
OUTPUT_NAME = "output.txt"

argLen = len(sys.argv)

print(argLen)

if argLen > 1:
	INPUT_NAME = sys.argv[1]

if argLen > 2:
	OUTPUT_NAME = sys.argv[2]

# Additional arguments are ignored

builder = txtbuilder.TXTB(INPUT_NAME)
builder.generateTxt(OUTPUT_NAME)
```

<br>

## How it works

The input is a text file separated into two sections, the data and the syntax. The data section is further separated into chunks, which are just Python string elements that will later be used to 'build' the final text document. Think bricks being used to build a house. The syntax section is about cherry-picking which data chunks will be outputted, and the order, as well as which transformations to apply on them, if any.

One-line comments are allowed in the syntax section.

If the syntax element reads `i`, then the output is the data element at index `i`. A Python list is used for this.

Syntax elements are **delimited by whitespace**. Any space added for readability won't affect the output. In most cases, the input file is human-readable, meaning that lines end with the newline. This trailing newline will show in the output, unless exlicitly removed.

- To get rid of trailing newlines use the `strip` pseudo-method. For example, taking the 6th element (`data[6]`) the syntax should be `6.strip`, making it equivalent to `data[6].strip()`.

  > Alternatively, remove newlines from the input file, as so: "value1%value2%value3")

<br>

### Character Sheet

Sytnax elements can be numbers (as seen above) or characters. They exist in a Python dictionary called **charmap**. For example, character `n` will result in `charmap['n']` which equals to `\n`. This is how **spaces**, **tabs** and **newlines** are inserted. If the dictionary doesns't have a mapping for whatever is inserted, the text will show as it is, in the output.

- x - Any number within `[0, len(data)-1]`
- s - Space
- t - Tab
- n - Newline

<br>

### Pseudo Methods

Syntax elements can be followed by a dot and the name of a Python function. User-defined (pseudo) methods are stored in a dictionary called **function_map**. For example, `4.caps` will output the result of `caps(data[4])`. Consecutive calls are also possible, such as `3.strip.caps` with precedence from left to right. I like referring to using these methods as '**function-wrapping**'.

Some examples:

- strip - Same as Python's strip.
- rpl_newline - Replaces `\n ` with `\n`
- caps - To `.upper()`
- lower - To `.lower()`
- linktitle - Adds `- ` before the text
- title - `.title()`

> All functions are custom and 'wrap' some functionality, whether it's a custom function, a built-in or a lambda (although the latter is an antipattern). I initially built this program to format the description of my YouTube videos.

<br>

### User Prompts

Prompt the user for any text input and display a message. Execution stops, text is entered and by default it is sent as is to output. Example: `~ Genres ~` will print `Genres:` and wait for user input.

**Important**: Function wrapping works in different ways depending on which `~` it is applied on. Function wrap on the starting `~` will apply the transformations to the displayed message. Do it on the ending `~` and the changes are made to the user's input. Both can also be done, as show below. It even works inside user prompts.

Example:

`commands.txt`:
```
\n*\n
~.caps Is 1.strip a star? ~.lower
```

The console will display: `IS * A STAR?`

Let's assume the user types `YES`.

Output: `yes`

<br>

### Prompt generation for AI tools.

TXTB can be used to generate prompts for Midjourney by placing various phrases in one line separated by commas (CSV format). All values are added into a set. If we create two sets, we can then reference them inside a combination generator prompt (what a name!). The set references act as placeholders and the result will be all combinations of the base prompt but with each placeholder replaced by values from each set.

In short, it can create prompts with parameter combinations.

In the data section I create a set named 'fruit'
```
#fruit#
apple, banana, strawberry, dragon fruit
```

> Note how I wrote 'fruit' instead of 'fruits', because it makes more sense in the base prompt.


#### The fruit and drink sets example

Input file:
```
#fruit#
apple, banana, strawberry, dragon fruit
%
#drink#
milk, fancy cocktail, cold beer, milk
%%
@ The #fruit# and the #drink# on a brown table @
```

Output:
```
The apple and the cold beer on a brown table
The banana and the cold beer on a brown table
The dragon fruit and the cold beer on a brown table
The strawberry and the cold beer on a brown table
The apple and the fancy cocktail on a brown table
The banana and the fancy cocktail on a brown table
The dragon fruit and the fancy cocktail on a brown table
The strawberry and the fancy cocktail on a brown table
The apple and the milk on a brown table
The banana and the milk on a brown table
The dragon fruit and the milk on a brown table
The strawberry and the milk on a brown table

```

> Note that there has to be space after `@` as it's a special symbol that triggers this functionality. This: `@I was having a #fruit# and a #drink#@` won't work. Instead, do this: `@ I was having a #fruit# and a #drink# @`

<br>

### Recursive Mode

Work in progress :)

<br>

## Use cases
- Can generate any post caption for YouTube or Instagram, based on any template
- Generate hashtag combinations from various sets of hashtags
- Generate Midjourney and ChatGPT prompts by combining sets of words

**Todo**
- Recursive mode for experimentation on how a 'seed' will evolve over multiple iterations
- Generate ASCII or even Unicode art from images

**Software-engineering-wise todo**
- Exceptions rising & handling
- Support for huge files - scalability
- Formalize the syntax to avoid undefined behavior (I haven't tried breaking it in every possible way)
- Move all functions used in 'wrapping' in their own class to enable subclassing and additional definitions by the user

