a
    ���c;  �                   @   s   d d� Z dS )c                 C   s�   d\}}d\}}t | �t |� }}| D ]}||d 7 }||d 7 }q&|D ]}||d 7 }||d 7 }qHt|| d�}	t|| d�}
t|| d�}t|| d�}|||	|
| d d | d d d�|||||d d |d d d�d	�}t|� |S )
N)�    r   �total_sleep�total_yawns�   r   �day�����)r   r   Zaverage_sleepZaverage_yawns�start�end)�first�second)�len�round�print)Zdate_range_1Zdate_range_2Ztotal_sleep_1Ztotal_yawns_1Ztotal_sleep_2Ztotal_yawns_2Zdays_1Zdays_2r   Zaverage_sleep1Zaverage_yawns1Zaverage_sleep2Zaverage_yawns2�summary� r   �M   C:\Users\Dawid Gebert\Desktop\studia\Projekt zespołowy\grupa-2\utils\main.py�lifestyle_summary   s<    

�


��r   N)r   r   r   r   r   �<module>   �    