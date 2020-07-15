"""This is a module for comprehending cases in different languages"""

from abc import ABC, abstractmethod


class Word(ABC):
    """Abstract class for a noun. Has abstract methods with converting a noun
    to all possible cases in all added language. In methods docstrings there
    are sentences with example of usage of these cases"""

    @abstractmethod
    def __init__(self, word):
        """Initiate a word"""
        self.word = word

    @abstractmethod
    def cased_by_number(self, number: int, if_one_then_accusative=False):
        """Get case by the number"""

    @abstractmethod
    def nominative_singular(self):
        """There is a dog"""
        return self.word

    @abstractmethod
    def nominative_plural(self):
        """There are dogs"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'

    @abstractmethod
    def genitive_singular(self):
        """There is no dog"""
        return self.word

    @abstractmethod
    def genitive_plural(self):
        """There are no dogs"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'

    @abstractmethod
    def accusative_singular(self):
        """I see/blame a dog"""
        return self.word

    @abstractmethod
    def accusative_plural(self):
        """I see/blame dogs"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'

    @abstractmethod
    def dative_singular(self):
        """I give something to a dog"""
        return self.word

    @abstractmethod
    def dative_plural(self):
        """I give something to dogs"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'

    @abstractmethod
    def instrumental_singular(self):
        """I'm drawing with pencil"""
        return self.word

    @abstractmethod
    def instrumental_plural(self):
        """I'm drawing with pencils"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'

    @abstractmethod
    def prepositional_singular(self):
        """I'm thinking about a dog"""
        return self.word

    @abstractmethod
    def prepositional_plural(self):
        """I'm thinking about dogs"""
        if self.word[-1] == 's':
            return self.word + "'"
        return self.word + 's'


class EnglishWord(Word):
    """Class for an English word"""

    def __init__(self, word):
        Word.__init__(self, word)

    def cased_by_number(self, number: int, if_one_then_accusative=False):
        """Get case by the number"""

    def nominative_singular(self):
        """There is a dog"""

    def nominative_plural(self):
        """There are dogs"""

    def genitive_singular(self):
        """There is no dog"""

    def genitive_plural(self):
        """There are no dogs"""

    def accusative_singular(self):
        """I see/blame a dog"""

    def accusative_plural(self):
        """I see/blame dogs"""

    def dative_singular(self):
        """I give something to a dog"""

    def dative_plural(self):
        """I give something to dogs"""

    def instrumental_singular(self):
        """I'm drawing with pencil"""

    def instrumental_plural(self):
        """I'm drawing with pencils"""

    def prepositional_singular(self):
        """I'm thinking about a dog"""

    def prepositional_plural(self):
        """I'm thinking about dogs"""


class RussianWord(Word):
    """Class for a Russian word"""

    def __init__(self, word):
        Word.__init__(self, word)

        self.end = ''
        if word[-1] in 'аьй':
            self.end = word[-1]

    def cased_by_number(self, number, if_one_then_accusative=False):
        """Get case by the number"""
        if number % 10 == 1 and not 10 <= number <= 20:  # 1, 21, 31, 41
            if if_one_then_accusative:
                return self.accusative_singular()
            return self.nominative_singular()
        if number % 10 in (2, 3, 4):  # 2, 23, 34
            return self.genitive_singular()
        return self.genitive_plural()  # 45, 6, 7, 11, 12, 19

    def print_all_possibles(self):
        """Print all the cases"""
        print("Есть", self.nominative_singular(), self.nominative_plural())
        print("Нет", self.genitive_singular(), self.genitive_plural())
        print("Виню", self.accusative_singular(), self.accusative_plural())
        #  print("Даю", self.dative_singular(), self.dative_plural())
        #  print("Творю", self.instrumental_singular(), self.instrumental_plural())
        #  print("Думаю о", self.prepositional_singular(), self.prepositional_plural())

    def nominative_singular(self):
        """Есть собака"""
        return self.word

    def nominative_plural(self):
        """Есть собаки"""
        if not self.end:
            return self.word + 'ы'  # стол -> столы
        if self.word[-2] in 'сртнл':
            return self.word[:-1] + 'ы'  # стена -> стены
        return self.word[:-1] + 'и'  # кошка -> кошки

    def genitive_singular(self):
        """Нет собаки"""
        if not self.end:
            return self.word + 'а'  # стол -> стола
        if self.end == 'а':
            if self.word[-2] in 'сртнл':
                return self.word[:-1] + 'ы'  # стена -> стены
            return self.word[:-1] + 'и'  # кошка -> кошки
        if self.end == 'ь':
            return self.word[:-1] + 'и'  # девственность - девстенности
        return self.word[:-1] + 'я'  # злодей -> злодея

    def genitive_plural(self):
        """Нет собак"""
        if not self.end:
            return self.word + 'ов'  # стол - столов
        if self.end == 'а':
            return self.word[:-1]
        if self.end == 'ь':
            return self.word[:-1] + 'ей'
        if self.end == 'й':
            return self.word[:-1] + 'ев'  # злодей -> злодеев
        raise ValueError("Word has wrong ending")

    def accusative_singular(self):
        """Виню собаку"""
        if self.end == 'а':
            return self.word[:-1] + 'у'
        return self.word

    def accusative_plural(self):
        """Виню собак"""

    def dative_singular(self):
        """Даю собаке"""

    def dative_plural(self):
        """Даю собакам"""

    def instrumental_singular(self):
        """Я рисую карандашом"""

    def instrumental_plural(self):
        """Я рисую карандашами"""

    def prepositional_singular(self):
        """Я думаю о собаке"""

    def prepositional_plural(self):
        """Я думаю о собаках"""


def get_word_object(word: str, language: str) -> Word:
    """
    :param word: word text
    :param language: word language (English, Russian)
    :return: Word object
    :rtype: Word
    """
    if language in ('ru', 'Ru', 'Russian', 'russian'):
        return RussianWord(word)
    if language in ('en', 'En', 'English', 'english'):
        return EnglishWord(word)
    raise ValueError(f"Unknown language: {language}")


if __name__ == '__main__':
    for test_word in ('стена', 'модер', 'кошка', 'дерево', 'злодей'):
        russian_word = RussianWord(test_word)
        russian_word.print_all_possibles()
        print()
