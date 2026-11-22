# tam v3.1 character-set cleanup report

Unicharset entries: v3 214 -> v3.1 186 (36 removed, 8 added)

## Removed from the unicharset

| Char | Code points | Name |
|---|---|---|
| `'்\u200c'` | U+0BCD U+200C | TAMIL SIGN VIRAMA + ZERO WIDTH NON-JOINER |
| `'※'` | U+203B | REFERENCE MARK |
| `'\x93'` | U+0093 | U+0093 |
| `'\x94'` | U+0094 | U+0094 |
| `'★'` | U+2605 | BLACK STAR |
| `'❍'` | U+274D | SHADOWED WHITE CIRCLE |
| `'✽'` | U+273D | HEAVY TEARDROP-SPOKED ASTERISK |
| `'ǃ'` | U+01C3 | LATIN LETTER RETROFLEX CLICK |
| `'画'` | U+753B | CJK UNIFIED IDEOGRAPH-753B |
| `'口'` | U+53E3 | CJK UNIFIED IDEOGRAPH-53E3 |
| `'即'` | U+5373 | CJK UNIFIED IDEOGRAPH-5373 |
| `'λ'` | U+03BB | GREEK SMALL LETTER LAMDA |
| `'í'` | U+00ED | LATIN SMALL LETTER I WITH ACUTE |
| `'●'` | U+25CF | BLACK CIRCLE |
| `'♦'` | U+2666 | BLACK DIAMOND SUIT |
| `'⅛'` | U+215B | VULGAR FRACTION ONE EIGHTH |
| `'☐'` | U+2610 | BALLOT BOX |
| `'✲'` | U+2732 | OPEN CENTRE ASTERISK |
| `'А'` | U+0410 | CYRILLIC CAPITAL LETTER A |
| `'소'` | U+C18C | HANGUL SYLLABLE SO |
| `'❖'` | U+2756 | BLACK DIAMOND MINUS WHITE X |
| `'ഖ'` | U+0D16 | MALAYALAM LETTER KHA |
| `'¡'` | U+00A1 | INVERTED EXCLAMATION MARK |
| `'→'` | U+2192 | RIGHTWARDS ARROW |
| `'Ѕ'` | U+0405 | CYRILLIC CAPITAL LETTER DZE |
| `'❋'` | U+274B | HEAVY EIGHT TEARDROP-SPOKED PROPELLER ASTERISK |
| `'·'` | U+00B7 | MIDDLE DOT |
| `'´'` | U+00B4 | ACUTE ACCENT |
| `'√'` | U+221A | SQUARE ROOT |
| `'Ꮩ'` | U+13D9 | CHEROKEE LETTER DO |
| `'◯'` | U+25EF | LARGE CIRCLE |
| `'。'` | U+3002 | IDEOGRAPHIC FULL STOP |
| `'翰'` | U+7FF0 | CJK UNIFIED IDEOGRAPH-7FF0 |
| `'²'` | U+00B2 | SUPERSCRIPT TWO |
| `'✤'` | U+2724 | HEAVY FOUR BALLOON-SPOKED ASTERISK |
| `'變'` | U+8B8A | CJK UNIFIED IDEOGRAPH-8B8A |

## Added to the unicharset

| Char | Code point | Name |
|---|---|---|
| ^ | U+005E | CIRCUMFLEX ACCENT |
| ` | U+0060 | GRAVE ACCENT |
| × | U+00D7 | MULTIPLICATION SIGN |
| ௐ | U+0BD0 | TAMIL OM |
| ௶ | U+0BF6 | TAMIL DEBIT SIGN |
| ௷ | U+0BF7 | TAMIL CREDIT SIGN |
| ௹ | U+0BF9 | TAMIL RUPEE SIGN |
| ௺ | U+0BFA | TAMIL NUMBER SIGN |

## Dictionary lists (after NFC, removing U+200C/U+200D, dropping entries with removed chars)

- words: 366671 entries kept, 0 dropped
- puncs: 308 entries kept, 0 dropped
- numbers: 60 entries kept, 0 dropped

## Training text

- lines kept: 149785; lines dropped (over 20% of words had removed chars, or too short): 224
- words dropped inside kept lines: 1335
- most frequent removed characters: '☐' U+2610 x95, '✽' U+273D x90, 'ا' U+0627 x71, '◯' U+25EF x66, '❖' U+2756 x62, '★' U+2605 x59, 'ा' U+093E x54, 'а' U+0430 x52, 'и' U+0438 x39, 'ر' U+0631 x37, 'ي' U+064A x34, '❋' U+274B x33, 'ā' U+0101 x33, 'н' U+043D x31, 'е' U+0435 x30, 'م' U+0645 x30, 'ˈ' U+02C8 x30, 'ل' U+0644 x29, 'र' U+0930 x27, '●' U+25CF x26, '♦' U+2666 x26, '්' U+0DCA x26, 'α' U+03B1 x26, 'о' U+043E x25, '́' U+0301 x25
