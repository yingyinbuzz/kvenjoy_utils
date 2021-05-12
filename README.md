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
| # Glyphs    | Integer           | 4    | Number of zipped glyphs                             |
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

A
[CBC](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_block_chaining_(CBC))
like algorithm is used to encrypt/decrypt bigger chunk of data.

**Encryption**:<br>
C<sub>i</sub> = (P<sub>i-1</sub> ⊕ C<sub>i-2</sub>) ⊕ E<sub>K</sub>(P<sub>i</sub> ⊕ C<sub>i-1</sub>)<br>
C<sub>0</sub> = [0, 0, 0, 0, 0, 0, 0, 0]<br>
P<sub>0</sub> = [0, 0, 0, 0, 0, 0, 0, 0]

**Decryption**:<br>
P<sub>i</sub> = C<sub>i-1</sub> ⊕ D<sub>K</sub>(C<sub>i</sub> ⊕ P<sub>i-1</sub>)<br>
C<sub>0</sub> = [0, 0, 0, 0, 0, 0, 0, 0]<br>
P<sub>0</sub> = [0, 0, 0, 0, 0, 0, 0, 0]

#### Brief steps of encryption
* Input
    * Plaintext buffer (arbitrary size)
    * Key buffer (128 bits) as `KEY`
* Padding plaintext buffer
    * Increase buffer size by 10 and pad it to be multiple of 8, after the new
        buffer should look like this:
        * Indicator (1 byte), contains `0x20 | PADDING_LENGTH`.
        * Padding (0-7 byte(s)), contains random numbers in range [50-127].
        * Prefix (2 bytes), contains random numbers in range [50-127].
        * Original plaintext (N bytes)
        * Postfix (7 bytes), contains zeros.
* Initialize a 8-byte-long last plaintext block (`LPB`) to all zeros.
* Initialize a 8-byte-long last ciphertext block (`LCB`) to all zeros.
* Encrypt prepared buffer, for each 8-byte block (`PB`) in plaintext buffer:
    * Xor `PB` and `LCB`,  put result in `CPB`.
    * Feed `CPB` and `KEY` to TEA(encrypt), put result in `LCB`.
    * Xor `LCB` and `LPB`, put result in `LCB`, append result to cipher buffer.
    * Copy `CPB` to `LPB`

#### Brief steps of decryption
* Input
    * Ciphertext buffer (arbitrary size)
    * Key buffer (128 bits) as `KEY`
* Initialize a 8-byte-long last plaintext block (`LPB`) to all zeros.
* Initialize a 8-byte-long last ciphertext block (`LCB`) to all zeros.
* Decrypt ciphertext buffer, for each 8-byte block (`CB`) in ciphertext buffer:
    * Xor `CB` and `LPB`,  put result in `CCB`.
    * Feed `CCB` and `KEY` to TEA(decrypt), put result in `LPB`.
    * Xor `LPB` and `LCB`, append result to plaintext buffer.
    * Copy `CB` to `LCB`
* Extract final plaintext buffer
    * Read the indicator byte, extract padding size (`PADDING_LENGTH`).
    * Calculate final plaintext size (`PLAIN_LENGTH = CIPHER_LENGTH - PADDING_LENGTH - 10`).
    * Skip `PADDING_LENGTH` padding bytes.
    * Skip two bytes prefix.
    * Extract `PLAIN_LENGTH` as final plaintext buffer.
