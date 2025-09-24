import 'package:flutter_test/flutter_test.dart';
import 'package:student_marketplace/models/faculty_filter_model.dart';

void main() {
  group('FacultyFilter Tests', () {
         test('should create faculty filter with correct properties', () {
       final faculty = FacultyFilter(
         name: 'test_faculty',
         displayName: 'Test Faculty',
         isSelected: false,
       );

       expect(faculty.name, 'test_faculty');
       expect(faculty.displayName, 'Test Faculty');
       expect(faculty.isSelected, false);
     });

         test('should copy faculty filter with new values', () {
       final original = FacultyFilter(
         name: 'test_faculty',
         displayName: 'Test Faculty',
         isSelected: false,
       );

       final copied = original.copyWith(
         isSelected: true,
       );

       expect(copied.name, original.name);
       expect(copied.displayName, original.displayName);
       expect(copied.isSelected, true);
     });
  });

  group('FacultyFilterManager Tests', () {
    setUp(() {
      // Reset all faculties before each test
      FacultyFilterManager.resetAll();
    });

    test('should have correct number of faculties', () {
      expect(FacultyFilterManager.faculties.length, 4);
    });

         test('should have correct faculty names', () {
       final facultyNames = FacultyFilterManager.faculties
           .map((f) => f.name)
           .toList();
       
       expect(facultyNames, [
         'humanities',
         'health_environmental',
         'FEBIT',
         'management_science',
       ]);
     });

    test('should return empty list when no product categories selected', () {
      final selectedCategories = FacultyFilterManager.getSelectedProductCategories();
      expect(selectedCategories, isEmpty);
    });

    test('should return selected product categories', () {
      // Add some product categories
      FacultyFilterManager.selectedProductCategories.add('Books');
      FacultyFilterManager.selectedProductCategories.add('Electronics');
      
      final selectedCategories = FacultyFilterManager.getSelectedProductCategories();
      expect(selectedCategories, containsAll(['Books', 'Electronics']));
    });

    test('should handle product category selection and removal', () {
      // Add and remove product categories
      FacultyFilterManager.selectedProductCategories.add('Books');
      FacultyFilterManager.selectedProductCategories.add('Electronics');
      FacultyFilterManager.selectedProductCategories.remove('Books');
      
      final selectedCategories = FacultyFilterManager.getSelectedProductCategories();
      expect(selectedCategories, contains('Electronics'));
      expect(selectedCategories, isNot(contains('Books')));
    });

    test('should select all faculties', () {
      FacultyFilterManager.selectAll();
      
      for (var faculty in FacultyFilterManager.faculties) {
        expect(faculty.isSelected, true);
      }
    });

    test('should reset all faculties', () {
      // First select all
      FacultyFilterManager.selectAll();
      
      // Then reset
      FacultyFilterManager.resetAll();
      
      for (var faculty in FacultyFilterManager.faculties) {
        expect(faculty.isSelected, false);
      }
    });

    test('should correctly identify if faculties are selected', () {
      expect(FacultyFilterManager.hasSelectedFaculties, false);
      
      FacultyFilterManager.faculties[0].isSelected = true;
      expect(FacultyFilterManager.hasSelectedFaculties, true);
    });

    test('should return selected faculties', () {
      FacultyFilterManager.faculties[0].isSelected = true;
      FacultyFilterManager.faculties[1].isSelected = true;
      
      final selectedFaculties = FacultyFilterManager.getSelectedFaculties();
      expect(selectedFaculties.length, 2);
      expect(selectedFaculties[0].name, 'humanities');
      expect(selectedFaculties[1].name, 'health_environmental');
    });

    test('should check if product categories are selected', () {
      expect(FacultyFilterManager.hasSelectedProductCategories, false);
      
      FacultyFilterManager.selectedProductCategories.add('Books');
      expect(FacultyFilterManager.hasSelectedProductCategories, true);
    });

    test('should clear product categories', () {
      FacultyFilterManager.selectedProductCategories.add('Books');
      FacultyFilterManager.selectedProductCategories.add('Electronics');
      
      FacultyFilterManager.clearProductCategories();
      expect(FacultyFilterManager.selectedProductCategories, isEmpty);
    });

    test('should select all product categories', () {
      FacultyFilterManager.selectAllProductCategories();
      
      final expectedCategories = [
        'Books', 'Electronics', 'Clothing', 'Furniture',
        'Appliances', 'Sports', 'Beauty', 'Other'
      ];
      
      for (var category in expectedCategories) {
        expect(FacultyFilterManager.selectedProductCategories, contains(category));
      }
    });
  });
}
