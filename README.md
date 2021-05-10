# Kvenjoy GFONT/GAP utilities

## File formats
By default all data fields below are in *big endian* byte order unless specified
individually.

### GFONT file
| Name          | Type    | Size | Description                                                    |
| --            | --      | :-:  | --                                                             |
| Version       | Integer | 4    | Font format version (up to version 7 so far)                   |
| Header size   | Integer | 4    | Size of following header block (in bytes)                      |
| Header        | Block   | *    | Font header, see [details](#header)                            |
| # Glyphs      | Integer | 4    | Number following glyph records(at most 30)                     |
| Glyphs        | Block   | *    | List of glyphs, see [details](#glyph)                          |
| Zipped glyphs | Block   | *    | Zip archive contains all glyphs, see [details](#zipped-glyphs) |

#### Header
From font format version 5 the header will be
[encrypted/decrypted](#encryptiondecryption) before being saved to/loaded from a
file.

| Name        | Type              | Size | Description                                         |
| --          | --                | :-:  | --                                                  |
| Vendor      | [String](#string) | *    | Vendor name? (always be `kvenjoy`)                  |
| Type        | Integer           | 4    | See [font type enumeration](#font-type-enumeration) |
| Name        | [String](#string) | *    | Font name                                           |
| Author      | [String](#string) | *    | Font author name                                    |
| Description | [String](#string) | *    | Font description                                    |
| Glyph size  | Integer           | 4    | Size boundary of individual glyphs?                 |
| # Glyphs?   | Integer           | 4    | ?                                                   |
| Password    | [String](#string) | *    | Font password (requires format version >=2)         |
| ?           | [String](#string) | *    | Always empty (requires format version >=4)          |
| UUID        | [String](#string) | *    | Font UUID (requires format version >=7)             |

#### Font type enumeration
| Value | Definition   |
| --    | --           |
| 0     | Chinese 2500 |
| 1     | English      |
| 2     | Chinese 3500 |
| 3     | Empty/Blank  |
| 4     | Chinese 6900 |
| 5     | Korean       |

#### Glyph
| Name       | Type    | Size | Description                  |
| --         | --      | :-:  | --                           |
| Code       | Short   | 2    | Unicode char of the glyph    |
| # Floats   | Integer | 4    | Number of following floats   |
| Floats     | Float   | *    | Floats                       |
| # Commands | Byte    | *    | Number of following commands |
| Commands   | Byte    | *    | Byte commands                |

Each glyph has an associated unicode number and several *strokes*. A *stroke*
designates the path travelled between a pen down and pen up (a continuous mark
on the paper); each *stroke* contains several *[points](#point)* and/or *[Bezier
points](#bezier-point)*.

By iterating and executing command in *Commands* buffer one could rebuild
*strokes* from *Floats* buffer.

##### Command
| Value | Definition                                            |
| --    | --                                                    |
| 0     | Start a new stroke                                    |
| 1     | Add a [point](#point) to current stroke               |
| 2     | Add a [Bezier point](#bezier-point) to current stroke |

##### Point
| Name | Type  | Size | Description               |
| --   | --    | :-:  | --                        |
| X    | Float | 4    | X coordinate of the point |
| Y    | Float | 4    | Y coordinate of the point |

##### Bezier point
| Name | Type  | Size | Description                              |
| --   | --    | :-:  | --                                       |
| CX1  | Float | 4    | X coordinate of the first control point  |
| CY1  | Float | 4    | Y coordinate of the first control point  |
| CX2  | Float | 4    | X coordinate of the second control point |
| CY2  | Float | 4    | Y coordinate of the second control point |
| X    | Float | 4    | X coordinate of the point                |
| Y    | Float | 4    | Y coordinate of the point                |

#### Zipped glyphs
A ZIP archive for glyphs, each zipped file has a file name of glyph unicode in
decimal, and it's content contains corresponding [glyph](#glyph) definition.

### String
| Name    | Type  | Size | Description                                 |
| --      | --    | :-:  | --                                          |
| Size    | Short | 2    | Size of following string content (in bytes) |
| Content | Byte  | *    | String content                              |

### Encryption/Decryption

A 16-round [TEA](https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm) is
used to encrypt/decrypt a 8-byte data block.

#### Brief steps of encryption
* Input: a plaintext buffer and a 128-bit key (`KEY`).
* Create a new buffer(`PB`) which is 10 bytes larger than given plaintext buffer.
* Calculate padding size(`PADDING_LENGTH`) for `PB` so it will contain multiple 8-byte blocks.
* Append an indicator byte to `PB` (`0x20 | PADDING_LENGTH`).
* Append `PADDING_LENGTH` random salt bytes to `PB`.
* Append at most 2 more random salt bytes (make sure length of `PB` doesn't
    exceed 8 bytes, only the first 8-byte block contains salt bytes).
* Append plaintext to `PB`.
* Append zero bytes to `PB` if there are space left.
* Initialize a 8-byte all-zero block to hold last ciphertext block (`LCB`).
* Initialize a 8-byte all-zero block to hold last plaintext block (`LPB`).
* Initialize a 8-byte all-zero block to hold current plaintext block (`CPB`).
* Split `PB` into several 8-byte blocks, for each block (`RPB`):
    * Xor `RPB` and `LCB`, put result in `CPB`.
    * Feed `CPB` and `KEY` to TEA(encrypt) and put result in `LCB`
    * Xor `LCB` and `LPB`, append result to final ciphertext buffer.
    * Copy `CPB` to `LPB`

#### Brief steps of decryption
* Input: a ciphertext buffer and a 128-bit key (`KEY`).
* Size of given ciphertext buffer should be multiple of 8.
* Initialize a 8-byte all-zero block to hold last ciphertext block (`LCB`).
* Initialize a 8-byte all-zero block to hold last plaintext block (`LPB`).
* Initialize a 8-byte all-zero block to hold current plaintext block (`CCB`).
* Initialize an empty buffer (`PB`).
* Split ciphertext buffer into several 8-byte blocks, for each block (`RCB`):
    * Xor `RCB` and `LPB`, put result in `CCB`.
    * Feed `CCB` and `KEY` to TEA(decrypt) and put result in `LPB`.
    * Xor `LPB` and `LCB`, append result to `PB`.
* Read indicator byte from `PB` and derive padding size(`PADDING_LENGTH`), skip
    `PADDING_LENGTH` salt bytes and at most 2 more salt bytes (see corresponding
    steps in [encryption](#brief-steps-of-encryption)), remaining bytes in `PB`
    is the final decrypted plaintext.
