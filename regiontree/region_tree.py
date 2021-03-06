from geonames_api.geonames_api import GeonamesAPI
from geonames_api.model.coordinate import Coordinate
from geonames_api.model.region import Region


class RegionTree:
    def __init__(self, api: GeonamesAPI):
        self.EARTH = Region(6295630, 'Earth', 'Earth', Coordinate(0, 0))

        self.api = api
        self.tree = self.build_world_tree()

    def get_region(self, geoname_id) -> Region:
        if geoname_id == self.EARTH.geoname_id:
            return self.EARTH
        for continent in self.tree.children:
            if geoname_id == continent.geoname_id:
                return continent
            for country in continent.children:
                if geoname_id == country.geoname_id:
                    return country
                for state in country.children:
                    if geoname_id == state.geoname_id:
                        return state
        raise ValueError(f"Could not find any region with id == {geoname_id} in the region tree!")

    def get_children(self, region: Region) -> set:
        return self.api.children(region.geoname_id)

    def get_countries(self) -> list:
        countries_of_the_world = list()
        for continent in self.get_children(self.EARTH):
            for country in self.get_children(continent):
                countries_of_the_world.append(country)
        return countries_of_the_world

    def build_world_tree(self) -> Region:
        for continent in self.get_children(self.EARTH):
            self.EARTH.add_children(continent)
            for country in self.get_children(continent):
                continent.add_children(country)
                for state in self.get_children(country):
                    country.add_children(state)
        return self.EARTH

    def print_region_tree(self, out_file='worldtree.txt'):
        number_countries: int = 0
        number_states: int = 0
        with open(out_file, 'w', 1, "UTF-8", 'strict') as tree_file:
            print(self.tree, file=tree_file)
            indent = "  "
            for continent in self.tree:
                level = 1
                print(level * indent + str(continent), file=tree_file)
                for country in continent:
                    level = 2
                    print(level * indent + str(country), file=tree_file)
                    number_countries += 1
                    for state in country:
                        level = 3
                        print(level * indent + str(state), file=tree_file)
                        number_states += 1

            print('Num countries : %d, num states: %d' % (number_countries, number_states), file=tree_file)

    def dot_country_tree(self, out_file='worldtree.dot'):
        """
        Writes a tree of the continents and the countries to the out_file
        :param out_file:
        :return:
        """
        with open(out_file, 'w', 1, "UTF-8", 'strict') as tree_file:
            print('digraph worldtree {', file=tree_file)
            for continent in self.tree:
                print(f'"{self.EARTH}" -> "{continent}";', file=tree_file)
                for country in continent:
                    print(f'"{continent}" -> "{country}";', file=tree_file)
            print('}', file=tree_file)

    def dot_continent_trees(self):
        """
        Writes several dot files names after the continents. These contain the continent tree including countries and sub-regions.
        :return:
        """
        for continent in self.tree:
            with open(f'{continent}.dot', 'w', 1, "UTF-8", 'strict') as tree_file:
                print(f'digraph {continent} {{', file=tree_file)
                print(f'"{self.EARTH}" -> "{continent}";', file=tree_file)
                for country in continent:
                    print(f'"{continent}" -> "{country}";', file=tree_file)
                    for state in country:
                        print(f'"{country}" -> "{state}";', file=tree_file)
                print('}', file=tree_file)
