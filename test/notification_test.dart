import 'package:flutter_test/flutter_test.dart';
import 'package:student_marketplace/models/notification_model.dart';

void main() {
  group('NotificationModel Tests', () {
    test('should create notification from JSON with string ID', () {
      final json = {
        'id': '123',
        'user_id': '456',
        'message': 'Test notification',
        'is_read': false,
        'created_at': '2023-01-01T00:00:00.000Z',
      };

      final notification = NotificationModel.fromJson(json);

      expect(notification.id, 123);
      expect(notification.userId, 456);
      expect(notification.message, 'Test notification');
      expect(notification.isRead, false);
      expect(notification.createdAt, DateTime.parse('2023-01-01T00:00:00.000Z'));
    });

    test('should create notification from JSON with integer ID', () {
      final json = {
        'id': 123,
        'user_id': 456,
        'message': 'Test notification',
        'is_read': true,
        'created_at': '2023-01-01T00:00:00.000Z',
      };

      final notification = NotificationModel.fromJson(json);

      expect(notification.id, 123);
      expect(notification.userId, 456);
      expect(notification.message, 'Test notification');
      expect(notification.isRead, true);
      expect(notification.createdAt, DateTime.parse('2023-01-01T00:00:00.000Z'));
    });

    test('should handle missing optional fields', () {
      final json = {
        'id': '123',
        'user_id': '456',
        'message': 'Test notification',
        'created_at': '2023-01-01T00:00:00.000Z',
      };

      final notification = NotificationModel.fromJson(json);

      expect(notification.id, 123);
      expect(notification.userId, 456);
      expect(notification.message, 'Test notification');
      expect(notification.isRead, false); // Default value
    });

    test('should copy notification with new values', () {
      final original = NotificationModel(
        id: 1,
        userId: 2,
        message: 'Original message',
        isRead: false,
        createdAt: DateTime.parse('2023-01-01T00:00:00.000Z'),
      );

      final copied = original.copyWith(
        isRead: true,
        message: 'Updated message',
      );

      expect(copied.id, original.id);
      expect(copied.userId, original.userId);
      expect(copied.message, 'Updated message');
      expect(copied.isRead, true);
      expect(copied.createdAt, original.createdAt);
    });
  });
}

