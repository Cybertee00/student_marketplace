import 'package:flutter_test/flutter_test.dart';
import 'package:student_marketplace/models/product_model.dart';
import 'package:student_marketplace/models/faculty_filter_model.dart';

void main() {
  group('Faculty Integration Tests', () {
    test('should create product with faculty and category', () {
      final product = Product(
        id: '1', title: 'Test Product', description: 'Test Description', price: 100.0,
        category: 'Electronics', faculty: 'FEBIT',
        images: ['image1.jpg'], sellerId: 'seller1', sellerName: 'John Doe', createdAt: DateTime.now(),
      );
      expect(product.faculty, 'FEBIT');
      expect(product.category, 'Electronics');
    });

    test('should parse product from JSON with faculty and category', () {
      final json = {
        'id': 1,
        'title': 'Test Product',
        'description': 'Test Description',
        'price': 100.0,
        'category': 'Books',
        'faculty': 'humanities',
        'images': ['image1.jpg'],
        'seller_id': 1,
        'seller': {'name': 'John', 'surname': 'Doe'},
        'created_at': '2023-01-01T00:00:00.000Z',
        'approved': true,
      };
      
      final product = Product.fromJson(json);
      expect(product.faculty, 'humanities');
      expect(product.category, 'Books');
    });

    test('should convert product to JSON with faculty and category', () {
      final product = Product(
        id: '1', title: 'Test Product', description: 'Test Description', price: 100.0,
        category: 'Furniture', faculty: 'management_science',
        images: ['image1.jpg'], sellerId: 'seller1', sellerName: 'John Doe', createdAt: DateTime.now(),
      );
      
      final json = product.toJson();
      expect(json['faculty'], 'management_science');
      expect(json['category'], 'Furniture');
    });

    test('should copy product with new faculty and category', () {
      final product = Product(
        id: '1', title: 'Test Product', description: 'Test Description', price: 100.0,
        category: 'Books', faculty: 'humanities',
        images: ['image1.jpg'], sellerId: 'seller1', sellerName: 'John Doe', createdAt: DateTime.now(),
      );
      
      final updatedProduct = product.copyWith(
        faculty: 'FEBIT',
        category: 'Electronics',
      );
      
      expect(updatedProduct.faculty, 'FEBIT');
      expect(updatedProduct.category, 'Electronics');
      expect(updatedProduct.title, 'Test Product'); // Other fields unchanged
    });

    test('should integrate with FacultyFilterManager', () {
      // Test that FacultyFilterManager can work with product categories
      FacultyFilterManager.resetAll();
      
      // Add some product categories to selection
      FacultyFilterManager.selectedProductCategories.add('Electronics');
      FacultyFilterManager.selectedProductCategories.add('Books');
      
      final selectedCategories = FacultyFilterManager.getSelectedProductCategories();
      expect(selectedCategories, contains('Electronics'));
      expect(selectedCategories, contains('Books'));
    });
  });
}
