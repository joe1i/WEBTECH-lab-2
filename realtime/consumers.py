import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import OnlineUser, UserActivity, RealtimeNotification
from announcements.models import Announcement

User = get_user_model()

class RealtimeConsumer(AsyncWebsocketConsumer):
    """Consumer для real-time функціональності"""
    
    async def connect(self):
        """Підключення користувача"""
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Додати користувача до групи онлайн користувачів
        self.online_group = 'online_users'
        await self.channel_layer.group_add(
            self.online_group,
            self.channel_name
        )
        
        # Додати користувача до персональної групи
        self.user_group = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Зареєструвати користувача як онлайн
        await self.set_user_online()

         # Надіслати початкові дані
        await self.send_initial_data()
        
        # Повідомити інших користувачів про підключення
        await self.broadcast_user_status('user_connected')
        
       
    
    async def disconnect(self, close_code):
        """Відключення користувача"""
        if hasattr(self, 'user') and self.user.is_authenticated:
            # Видалити користувача з онлайн статусу
            await self.set_user_offline()
            
            # Повідомити інших користувачів про відключення
            await self.broadcast_user_status('user_disconnected')
            
            # Покинути групи
            await self.channel_layer.group_discard(
                self.online_group,
                self.channel_name
            )
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Обробка повідомлень від клієнта"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.handle_ping()
            elif message_type == 'reaction_toggled':
                await self.handle_reaction_toggled(data)
            elif message_type == 'page_visit':
                await self.handle_page_visit(data)
            elif message_type == 'get_online_users':
                await self.send_online_users()
            else:
                await self.send_error('Unknown message type')
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')

    async def handle_ping(self):
        """Обробка ping повідомлень для підтримки з'єднання"""
        await self.update_user_activity()
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_reaction_toggled(self, data):
        """Обробка зміни реакції на оголошення"""
        announcement_id = data.get('announcement_id')
        if not announcement_id:
            return

        announcement = await self.get_announcement(announcement_id)
        if not announcement:
            return

        # Логувати активність
        await self.log_activity('reaction_change', f'Оновлено реакцію', {
            'announcement_id': announcement_id
        })


        counts = await self.get_announcement_reaction_counts(announcement_id)
        
        # Повідомити автора оголошення про реакцію
        if announcement.author != self.user:
            await self.send_user_notification(
                announcement.author.id,
                'new_reaction',
                f'{self.user.username} відреагував на ваше оголошення!'
            )

        # Повідомити всіх про оновлення реакції
        await self.channel_layer.group_send(
            self.online_group,
            {
                'type': 'reaction_update_notification',
                'announcement_id': announcement_id,
                'counts': counts,
                'user': self.user.username
            }
        )

    async def handle_page_visit(self, data):
        """Обробка відвідування сторінки"""
        page_url = data.get('url', '')
        page_title = data.get('title', '')
        
        # Оновити поточну сторінку користувача
        await self.update_user_page(page_url)
        
        # Логувати активність
        await self.log_activity('page_visit', f'Відвідав сторінку: {page_title}', {
            'url': page_url,
            'title': page_title
        })
    
    async def send_initial_data(self):
        """Надіслати початкові дані після підключення"""
        online_users = await self.get_online_users_data()

        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'online_users': online_users, 
            'user_id': self.user.id 
        }))
    
    async def send_online_users(self):
        """Надіслати список онлайн користувачів"""
        online_users = await self.get_online_users_data()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': online_users
        }))

    async def send_error(self, message):
        """Надіслати повідомлення про помилку"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    async def reaction_update_notification(self, event):
        """Відправка оновлених лічильників клієнту"""
        await self.send(text_data=json.dumps({
            'type': 'reaction_update',
            'announcement_id': event['announcement_id'],
            'counts': event['counts'],
            'user': event['user']
        }))

    async def user_notification(self, event):
        """Персональне сповіщення користувачу"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': event['notification_type'],
            'title': event['title'],
            'message': event['message'],
            'data': event['data']
        }))

    async def user_status_update(self, event):
        """Оновлення статусу користувача"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'action': event['action'],
            'user': event['user'],
            'online_count': event['online_count']
        }))

    # Допоміжні методи для роботи з базою даних
    @database_sync_to_async
    def set_user_online(self):
        """Встановити користувача як онлайн"""
        OnlineUser.objects.update_or_create(
            user=self.user,
            defaults={
                'channel_name': self.channel_name,
                'last_activity': timezone.now()
            }
        )
    
    @database_sync_to_async
    def set_user_offline(self):
        """Видалити користувача з онлайн статусу"""
        OnlineUser.objects.filter(user=self.user).delete()
    
    @database_sync_to_async
    def update_user_activity(self):
        """Оновити час останньої активності"""
        OnlineUser.objects.filter(user=self.user).update(
            last_activity=timezone.now()
        )
    
    @database_sync_to_async
    def update_user_page(self, page_url):
        """Оновити поточну сторінку користувача"""
        OnlineUser.objects.filter(user=self.user).update(
            page_url=page_url,
            last_activity=timezone.now()
        )

    @database_sync_to_async
    def log_activity(self, activity_type, description, metadata=None):
        """Логувати активність користувача"""
        UserActivity.objects.create(
            user=self.user,
            activity_type=activity_type,
            description=description,
            metadata=metadata or {}
        )

    @database_sync_to_async
    def get_online_users_data(self):
        """Отримати дані онлайн користувачів"""
        online_users = OnlineUser.get_online_users()
        return [
            {
                'id': ou.user.id,
                'username': ou.user.username,
                'full_name': ou.user.first_name, 
                'connected_at': ou.connected_at.isoformat(),
                'page_url': ou.page_url
            }
            for ou in online_users
        ]
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """Отримати непрочитані сповіщення"""
        notifications = RealtimeNotification.objects.filter(
            recipient=self.user,
            is_read=False
        )[:10]
        
        return [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'data': n.data,
                'created_at': n.created_at.isoformat()
            }
            for n in notifications
        ]
    
    @database_sync_to_async
    def serialize_user(self, user):
        """Серіалізувати користувача"""
        return {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name
        }
    
    @database_sync_to_async
    def get_announcement_reaction_counts(self, announcement_id):
        """Підрахунок реакцій"""
        from reactions.models import Reaction 
        
        return {
            'like': Reaction.objects.filter(announcement_id=announcement_id, reaction_type='like').count(),
            'fire': Reaction.objects.filter(announcement_id=announcement_id, reaction_type='fire').count(),
            'heart': Reaction.objects.filter(announcement_id=announcement_id, reaction_type='heart').count(),
            'sad': Reaction.objects.filter(announcement_id=announcement_id, reaction_type='sad').count(),
        }

    @database_sync_to_async
    def get_announcement(self, announcement_id):
        try:
            return Announcement.objects.select_related('author').get(id=announcement_id)
        except Announcement.DoesNotExist:
            return None
    
    async def broadcast_user_status(self, action):
        """Повідомити про зміну статусу користувача"""
        online_count = await database_sync_to_async(OnlineUser.get_online_count)()
        
        await self.channel_layer.group_send(
            self.online_group,
            {
                'type': 'user_status_update',
                'action': action,
                'user': await self.serialize_user(self.user),
                'online_count': online_count
            }
        )
    
    async def send_user_notification(self, user_id, notification_type, message, data=None):
        """Надіслати сповіщення конкретному користувачу"""
        # Зберегти в базі даних
        await self.create_notification(user_id, notification_type, message, data)
        
        # Надіслати через WebSocket
        await self.channel_layer.group_send(
            f'user_{user_id}',
            {
                'type': 'user_notification',
                'notification_type': notification_type,
                'title': 'Нове сповіщення',
                'message': message,
                'data': data or {}
            }
        )

    @database_sync_to_async
    def create_notification(self, user_id, notification_type, message, data=None):
        """Створити сповіщення в базі даних"""
        RealtimeNotification.objects.create(
            recipient_id=user_id,
            sender=self.user,
            notification_type=notification_type,
            title='Нове сповіщення',
            message=message,
            data=data or {}
        )