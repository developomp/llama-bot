# Contribution guide

## Table of contents

- [Contribution guide](#contribution-guide)
  - [Table of contents](#table-of-contents)
  - [Purpose](#purpose)
  - [Assumptions](#assumptions)
  - [Getting started](#getting-started)
    - [Development environment](#development-environment)
    - [Required knowledge](#required-knowledge)
    - [Bot](#bot)
    - [Web Interface](#web-interface)
    - [Documentation](#documentation)
  - [Commit message](#commit-message)
  - [Creating / updating a command](#creating--updating-a-command)
    - [Help message](#help-message)
    - [Structure](#structure)

## Purpose

There are several goals this guide aims to achieve:

- Help new contributors get started
- Prevent information fragmentation as people work on different parts of the software
- Streamline the development workflow
- Make things work in the project owner's absence
- Minimize intervention and back-and-forth communication (e.g. The contributor didn't format their code properly)

## Assumptions

All contributors are assumed to be familiar with the following:

- git (and by extension github and developer collaboration)
- node.js and its ecosystem (npm packages, yarn, etc.)
- javascript and typescript
- code formatting

## Getting started

### Development environment

Contributors are free to use whatever IDE they want but the usage of [vscode](https://code.visualstudio.com) is highly recommended.

Format markdown file(s) with [prettier](https://prettier.io) formatter

### Required knowledge

### Bot

- [discord.js](https://discord.js.org)
- [sapphire framework](https://www.sapphirejs.dev)

### Web Interface

- [express.js](https://expressjs.com)
- [passport.js](https://www.passportjs.org)
- [firebase functions](https://firebase.google.com/docs/functions)

### Documentation

- [Docusaurus](https://docusaurus.io)
- [Markdown](https://www.markdownguide.org/basic-syntax)

## Commit message

The commit message should be a clear and concise description of what the commit does.
The first line should be no more than 50 characters and the rest no more than 72.

## Creating / updating a command

Use the `CustomCommand` defined in [src/custom/CustomCommand.ts](./src/custom/CustomCommand.ts) instead of importing from `@sapphire/framework`.

### Help message

- consistent usage information

### Structure

- one export per command
  - functions should be `static` whenever possible
- Keep the `messageRun` function clean (ideally less than 50 lines).
- Separate regular imports from type imports.
- Separate the embedded message building process to a separate function.

  This also makes testing easier

- jsdoc comments should...

  - not include argument and return types.

    They should be included in the function instead.

  - not include a dash (`-`) in the `@returns` tag.

  Do this:

  ```ts
  /**
   * This function does something.
   *
   * - Here's some extra information
   *
   * @param argument - This is an argument.
   * @returns some string.
   */
  function someFunction(argument: string): string {
  	const someString = "some string"

  	return someString
  }
  ```

  Not this:

  ```ts
  /**
   * This function does something.
   *
   * - Here's some extra information
   *
   * @param {string} argument - This is an argument.
   * @returns {string}  - some string.
   */
  function someFunction(argument) {
  	const someString = "some string"

  	return someString
  }
  ```
