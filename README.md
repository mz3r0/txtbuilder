# TXTBuilder

TXTBuilder is a parser that works like a mini programming-language that can be used to generate social media post descriptions for YouTube or Instagram, text art or any Unicode text document that obeys a specific pattern.

Another use case is generating prompts for AI tools like Midjourney.

<br>

## How to run

Download the package, create your file `commands.txt`, creat the following script that imports TXTB and run it:

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

Behavior is controlled through the constants at the top of `__init__.py` and class members in `TXTB`.

<br>

## How it works

The input is a text file separated into two sections, the data and the syntax. The data seciton is further separated into chunks, which are just Python string elements that will later be used to 'build' the final text document, just like bricks are used to build a house. The syntax section is where you cherry-pick which data chunks will appear, in what order, and what transformations to apply on them, if any.

I also like referring to the data chunks as data fragments.

The syntax section allows single-line comments.

Internally, a list is created with the data elements. If a number `i` is read at input, then the output is the data element at index `i`.

Syntax elements are **delimited by whitespace** which doesn't affect the output. Almost all data elements end with a newline (if the input file is human-readable) which will show in the output. This is default. 

- To get rid of trailing newlines use the `strip` pseudo-method. For example, taking the 6th fragment (or `data[6]`) we type `6.strip`.

  > Another way to prevent this is keeping the data fragments in one line (similar to "frag1%frag2%frag3")

<br>

### Character Sheet

Sytnax elements can be numbers or characters. These characters exist in a special dictionary called **charmap**. For example, character `n` at input results in `charmap['n']` which equals to `\n`. This is how **spaces**, **tabs** and **newlines** are inserted. If the input character (or string) doesn't exist in this dictionary, it is sent to output as it is. To be more specific, in the syntax and outside user prompts, anything that isnt a numeric value or a charSheet key will be treated as a constant and will show up in the output.

- x - Any number within `[0, len(data)-1]`
- s - Space
- t - Tab
- n - Newline

<br>

### Pseudo Methods

Syntax elements can be followed by a dot and the name of a python function. I'll now refer to them simply as 'methods'. User-defined methods are stored in a dictionary called **function_map**. For example, `4.caps` will output the result of `caps(data[4])`. Consecutive calls are also possible, such as `3.strip.caps`.

Some examples:

- strip - Same as python's strip.
- rpl_newline - Replaces `\n ` with `\n`
- caps - To.upper()
- lower - To.lower()
- linktitle - Adds `- ` before the text
- title - Str.title()

> All functions are custom and 'wrap' some functionality, whether it's a custom function, a built-in or a lambda (although the latter is an antipattern). I initially built this program to format the description of my YouTube videos. I also like referring to using these special methods as '**function-wrapping**'.

<br>

### User Prompts

Prompt the user for any text input and display a message. Execution stops, text is entered and by default it is sent as is to output. Example: `~ Genres ~` will print `Genres:` and wait for user input.

Function wrapping works in different ways depending on which `~` it is applied on. Function wrap on the starting `~` will apply the transformations to the displayed message. Do it on the ending `~` and the changes are made to the user's input. Both can also be done, as show below. Function wrapping works inside user prompts too.

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

TXTB can be used to generate prompts for Midjourney by placing various phrases in one line separated by commas, basically CSV format. All values are added into a set. If we create two sets, we can then reference them inside a combination generator prompt (what a name!). The set references act as placeholders and the result will be all combinations of the base prompt but with each placeholder replaced by values from each set.

In short, it can create prompts with parameter combinations.

In the data section I create a set named 'fruit'
```
#fruit#
apple, banana, strawberry, dragon fruit
```

> Note how I wrote 'fruit' instead of 'fruits', because it makes more sense in the base prompt.


#### The fruit and drink sets example

The input:
```
#fruit#
apple, banana, strawberry, dragon fruit
%
#drink#
milk, fancy cocktail, cold beer, milk
%%
@ A #fruit# and a #drink# on a brown table @
```

The output:
```
A apple and a cold beer on a brown table
A banana and a cold beer on a brown table
A dragon fruit and a cold beer on a brown table
A strawberry and a cold beer on a brown table
A apple and a fancy cocktail on a brown table
A banana and a fancy cocktail on a brown table
A dragon fruit and a fancy cocktail on a brown table
A strawberry and a fancy cocktail on a brown table
A apple and a milk on a brown table
A banana and a milk on a brown table
A dragon fruit and a milk on a brown table
A strawberry and a milk on a brown table

```

> Note that `@I was having a #fruit# and a #drink#@` won't work, there has to be space after `@` as it's a special symbol that triggers this functionality. So, the correct form is `@ I was having a #fruit# and a #drink# @`

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

**Program-wise todo**
- Exceptions rising & handling
- Support for huge files - scalability
- Formalize the syntax to avoid undefined behavior (I haven't tried breaking it in every possible way)
- Move all functions used in 'wrapping' in their own class to enable subclassing and additional definitions by the user

